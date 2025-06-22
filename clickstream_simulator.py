# shadowtrail_fraud_detection/clickstream_simulator.py

import pandas as pd
import requests
import time
import random

# Load session dataset
df = pd.read_csv("user_sessions.csv")

# Simulate session aggregation per user
agg_df = df.groupby("user_id").agg({
    "latency_since_last_action": "mean",
    "geo_distance_from_last_ip": "sum",
    "device_switch_count": "max",
    "session_duration": "max"
}).reset_index()

# Randomize sending order
agg_df = agg_df.sample(frac=1).reset_index(drop=True)

url = "http://localhost:8000/score_session"  # Ensure FastAPI is running

for i, row in agg_df.iterrows():
    payload = {
        "latency_since_last_action": row["latency_since_last_action"],
        "geo_distance_from_last_ip": row["geo_distance_from_last_ip"],
        "device_switch_count": int(row["device_switch_count"]),
        "session_duration": row["session_duration"]
    }
    try:
        response = requests.post(url, json=payload)
        print(f"[{i+1}/{len(agg_df)}] User {row['user_id']} → {response.json()}")
    except Exception as e:
        print(f"Error with user {row['user_id']}: {e}")
    time.sleep(random.uniform(0.1, 0.5))  # simulate real-time arrival

