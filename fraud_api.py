# shadowtrail_fraud_detection/fraud_api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib as joblib
import numpy as np

app = FastAPI(title="ShadowTrail Fraud Scoring API")

# Load trained model
try:
    model = joblib.load("feature_modeling.joblib")
except FileNotFoundError:
    raise RuntimeError("Model file 'fraud_model.joblib' not found. Run feature_modeling.py first.")

# Define request schema
class SessionData(BaseModel):
    
    latency_since_last_action: float
    geo_distance_from_last_ip: float
    device_switch_count: int
    session_duration: float

# Risk thresholding logic
def risk_decision(score: float) -> str:
    if score > 0.8:
        return "Escalate to Fraud Team"
    elif score > 0.5:
        return "Flag for 2FA"
    else:
        return "Allow Transaction"

# Scoring endpoint
@app.post("/score_session")
def score_session(data: SessionData):
    try:
        features = np.array([[
            data.latency_since_last_action,
            data.geo_distance_from_last_ip,
            data.device_switch_count,
            data.session_duration
        ]])
        score = model.predict_proba(features)[0][1]
        decision = risk_decision(score)
        return {"risk_score": round(score, 3), "decision": decision}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
