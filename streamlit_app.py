import streamlit as st
import requests

st.title("🔍 ShadowTrail Fraud Detection Demo")

latency = st.slider("Latency Since Last Action (s)", 0.0, 10.0, 1.2)
geo_dist = st.slider("Geo Distance from Last IP (km)", 0.0, 1000.0, 50.0)
device_switch = st.slider("Device Switch Count", 0, 5, 1)
session_duration = st.slider("Session Duration (s)", 0.0, 3600.0, 300.0)

if st.button("Score Session"):
    data = {
        "latency_since_last_action": latency,
        "geo_distance_from_last_ip": geo_dist,
        "device_switch_count": device_switch,
        "session_duration": session_duration
    }

    try:
        response = requests.post("http://localhost:8000/score_session", json=data)
        result = response.json()
        st.success(f"🧠 Risk Score: {result['risk_score']} | Decision: {result['decision']}")
    except Exception as e:
        st.error(f"Error contacting API: {e}")
