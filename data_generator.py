# shadowtrail_fraud_detection/data_generator.py

import random
import uuid
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

random.seed(42)
np.random.seed(42)

# Define possible session actions
EVENTS = ["login", "browse", "add_to_cart", "checkout", "logout", "change_device", "location_switch", "contact_support"]

# Generate a synthetic user session
def generate_session(user_id, start_time):
    session_length = random.randint(4, 10)
    session = []
    timestamp = start_time
    last_ip = np.random.randint(100, 255)
    device_switch_count = 0
    geo_distance_total = 0
    suspicious_sequence = False

    action_sequence = []
    for _ in range(session_length):
        event = random.choice(EVENTS)
        latency = np.abs(np.random.normal(2, 0.5))
        timestamp += timedelta(seconds=latency)

        if event == "change_device":
            device_switch_count += 1

        geo_dist = np.abs(np.random.normal(10, 5)) if event == "location_switch" else 0
        geo_distance_total += geo_dist

        action_sequence.append(event)

        session.append({
            "user_id": user_id,
            "timestamp": timestamp,
            "event_type": event,
            "latency_since_last_action": latency,
            "geo_distance_from_last_ip": geo_dist,
            "device_switch_count": device_switch_count,  # updated dynamically
            "session_duration": (timestamp - start_time).total_seconds(),
            "label": 0  # temporarily 0, updated after pattern eval
        })

    risk_score = 0

    if action_sequence[:3] == ["login", "change_device", "checkout"]:
        risk_score += 1
    if device_switch_count >= 2:
        risk_score += 1
    if geo_distance_total > 50:
        risk_score += 1
    if session[-1]["session_duration"] < 20:
        risk_score += 1

# Label as fraud if risk_score >= 2
    if risk_score >= 2:
        for row in session:
            row["label"] = 1

    if suspicious_sequence:
        for row in session:
            row["label"] = 1

    return session

# Generate multiple sessions
def generate_sessions(n_users=2000):
    all_sessions = []
    base_time = datetime.now()
    for _ in range(n_users):
        user_id = str(uuid.uuid4())[:8]
        session_time = base_time + timedelta(minutes=random.randint(0, 10000))
        session = generate_session(user_id, session_time)
        all_sessions.extend(session)
    return pd.DataFrame(all_sessions)


if __name__ == "__main__":
    df = generate_sessions()
    df.to_csv("user_sessions.csv", index=False)
    print("Generated user_sessions.csv with shape:", df.shape)


# Exploratory plots
sns.countplot(data=df, x="event_type", hue="label")
plt.title("Event Type Distribution by Fraud Label")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

sns.boxplot(data=df, x="label", y="session_duration")
plt.title("Session Duration vs Fraud")
plt.tight_layout()
plt.show()

sns.boxplot(data=df, x="label", y="geo_distance_from_last_ip")
plt.title("Geo Distance vs Fraud")
plt.tight_layout()
plt.show()

