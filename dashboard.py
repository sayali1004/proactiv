# dashboard.py
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(layout="wide", page_title="ShadowTrail Fraud Dashboard")
st.title("🚨 ShadowTrail Real-Time Fraud Monitoring")

engine = create_engine("sqlite:///sessions.db")

def load_data():
    return pd.read_sql("SELECT * FROM sessions ORDER BY id DESC LIMIT 50", con=engine)

data = load_data()

def color_decision(val):
    if val == "Escalate to Fraud Team":
        return "background-color: red; color: white"
    elif val == "Flag for 2FA":
        return "background-color: orange; color: black"
    else:
        return ""

st.dataframe(data.style.applymap(color_decision, subset=["decision"]), use_container_width=True)
