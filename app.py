"""
Road Accident Analysis in India — Interactive Dashboard
Data source: MoRTH / OpenCity (2020-2024), Census 2011 population

Run locally with: streamlit run app.py
Deploy on Streamlit Community Cloud by pushing this + the /data folder to a GitHub repo.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import json

st.set_page_config(page_title="Road Accidents in India (2020-2024)", layout="wide")

# --- Load data ---
@st.cache_data
def load_data():
    state_merged = pd.read_csv("data/master_state_level.csv")
    collision_clean = pd.read_csv("data/type_of_collision_clean.csv")
    violation_clean = pd.read_csv("data/type_of_violation_clean.csv")
    time_interval_clean = pd.read_csv("data/time_interval_2020_2024.csv")
    month_wise_clean = pd.read_csv("data/month_wise_2020_2024.csv")
    with open("data/india_states.geojson") as f:
        india_geojson = json.load(f)
    return state_merged, collision_clean, violation_clean, time_interval_clean, month_wise_clean, india_geojson

state_merged, collision_clean, violation_clean, time_interval_clean, month_wise_clean, india_geojson = load_data()

# --- Title ---
st.title("🚦 Road Accident Analysis in India (2020-2024)")
st.markdown("Source: Ministry of Road Transport & Highways (MoRTH), via OpenCity | Population: Census 2011")

# --- Section 1: Choropleth ---
st.header("State-wise Accident Rate")

name_fix_for_map = {
    "Andaman & Nicobar Islands": "Andaman & Nicobar",
    "Dadra & Nagar Haveli and Daman & Diu": "Dadra and Nagar Haveli and Daman and Diu",
    "J & K": "Jammu & Kashmir",
}
state_merged['State_for_map'] = state_merged['State'].replace(name_fix_for_map)

fig_map = px.choropleth(
    state_merged,
    geojson=india_geojson,
    locations='State_for_map',
    featureidkey='properties.ST_NM',
    color='Accidents_per_lakh_2024',
    color_continuous_scale='Reds',
    hover_name='State',
    hover_data={'2024 Accidents': True, 'Accidents_per_lakh_2024': ':.1f', 'State_for_map': False},
    title='Accidents per Lakh Population, 2024'
)
fig_map.update_geos(fitbounds="locations", visible=False)
fig_map.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, height=550)
st.plotly_chart(fig_map, use_container_width=True)

st.markdown("""
**Key finding:** Goa has the highest accident rate per capita (~184 per lakh) despite ranking
near the bottom in raw accident count — nearly 5x Maharashtra's rate, despite Maharashtra
having 35x Goa's population and far more total accidents.
""")

# --- Section 2: National trend ---
st.header("National Trend, 2020-2024")
col1, col2 = st.columns(2)

with col1:
    year_cols_acc = ['2020 Accidents', '2021 Accidents', '2022 Accidents', '2023 Accidents', '2024 Accidents']
    years = [2020, 2021, 2022, 2023, 2024]
    national_accidents = state_merged[year_cols_acc].sum()
    fig_trend = px.line(x=years, y=national_accidents.values, markers=True,
                         labels={'x': 'Year', 'y': 'Accidents'}, title='National Accidents by Year')
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    fig_month = px.bar(month_wise_clean, x='Month', y='2024_Accidents',
                        title='2024 Accidents by Month')
    st.plotly_chart(fig_month, use_container_width=True)

st.markdown("""
**Key finding:** April 2020 shows a sharp dip (~8,400 accidents vs. a typical 30,000-40,000) —
this lines up with India's COVID-19 lockdown period, not a data error.
""")

# --- Section 3: Time of day ---
st.header("Time of Day Pattern")
fig_time = px.bar(time_interval_clean[time_interval_clean['Time_interval'] != 'Unknown Time'],
                   x='Time_interval', y='2024_Accidents', title='Accidents by Time Interval, 2024')
st.plotly_chart(fig_time, use_container_width=True)
st.markdown("**Key finding:** 18:00-21:00 hrs is consistently the peak window every year from 2020-2024, and its share of total accidents has been slowly rising (19.9% → 21.1%).")

# --- Section 4: Collision & violation severity ---
st.header("Severity by Collision & Violation Type")
col3, col4 = st.columns(2)

with col3:
    fig_collision = px.bar(collision_clean.sort_values('Fatality_rate', ascending=False),
                            x='Type of collision', y='Fatality_rate',
                            title='Fatality Rate by Collision Type (%)')
    st.plotly_chart(fig_collision, use_container_width=True)

with col4:
    violation_clean['2024-Accidents'] = violation_clean['2024-Accidents'].astype(str).str.replace(',', '').astype(float)
    violation_clean['2024-Killed'] = violation_clean['2024-Killed'].astype(str).str.replace(',', '').astype(float)
    violation_clean['Fatality_rate'] = violation_clean['2024-Killed'] / violation_clean['2024-Accidents'] * 100
    fig_violation = px.bar(violation_clean.sort_values('Fatality_rate', ascending=False),
                            x='Category', y='Fatality_rate',
                            title='Fatality Rate by Violation Type (%)')
    st.plotly_chart(fig_violation, use_container_width=True)

st.markdown("""
**Key finding:** Use of mobile phone is the least frequent violation category but has the
highest fatality rate (~41%) — higher than drunk driving or over-speeding, despite over-speeding
causing 70x more accidents in raw count.
""")

# --- Section 5: Top/Bottom states table ---
st.header("State Rankings")
col5, col6 = st.columns(2)
with col5:
    st.subheader("Top 10 by Raw Accident Count")
    st.dataframe(state_merged.nlargest(10, '2024 Accidents')[['State', '2024 Accidents']].reset_index(drop=True))
with col6:
    st.subheader("Top 10 by Accident Rate (per lakh population)")
    st.dataframe(state_merged.nlargest(10, 'Accidents_per_lakh_2024')[['State', 'Accidents_per_lakh_2024']].reset_index(drop=True))

st.markdown("---")
st.caption("Built as a data analytics portfolio project. Data: MoRTH Road Accidents in India 2024 report, via OpenCity and direct PDF extraction. Population: Census 2011.")
