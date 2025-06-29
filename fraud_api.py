# shadowtrail_fraud_detection/fraud_api.py
from fastapi import Request 
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import joblib as joblib
import numpy as np
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from alerts import send_email_alert
from sqlalchemy import create_engine, Column, Float, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker


app = FastAPI(title="ShadowTrail Fraud Scoring API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to ["http://localhost:5500"] for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Serve static files (e.g., HTML, JS, CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")
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
    
#Get root endpoint
templates = Jinja2Templates(directory="static")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


Base = declarative_base()
engine = create_engine("sqlite:///sessions.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

class SessionRecord(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    latency = Column(Float)
    geo = Column(Float)
    switch = Column(Integer)
    duration = Column(Float)
    score = Column(Float)
    decision = Column(String)

Base.metadata.create_all(bind=engine)


# Scoring endpoint
@app.post("/score_session")
def get_score_session(data: SessionData):
    try:
        features = np.array([[
            data.latency_since_last_action,
            data.geo_distance_from_last_ip,
            data.device_switch_count,
            data.session_duration
        ]])
        score = model.predict_proba(features)[0][1]
        decision = risk_decision(score)
        # Store session in the DB
        db = SessionLocal()
        session_record = SessionRecord(
        latency=data.latency_since_last_action,
        geo=data.geo_distance_from_last_ip,
        switch=data.device_switch_count,
        duration=data.session_duration,
        score=round(score, 3),
        decision=decision
)
        db.add(session_record)
        db.commit()
        db.close()

        return {"risk_score": round(score, 3), "decision": decision}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
