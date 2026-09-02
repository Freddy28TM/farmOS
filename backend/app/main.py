from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from backend.app.decision_engine import assess_water_risk


app = FastAPI(title="FarmOS API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class WaterRiskRequest(BaseModel):
    recent_rainfall: float
    forecast_rainfall: float
    temperature: float


@app.get("/")
def root():
    return {"message": "FarmOS API is running"}


@app.post("/water-risk")
def water_risk(request: WaterRiskRequest):
    return assess_water_risk(
        recent_rainfall=request.recent_rainfall,
        forecast_rainfall=request.forecast_rainfall,
        temperature=request.temperature,
    )