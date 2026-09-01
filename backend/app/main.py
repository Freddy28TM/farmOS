from fastapi import FastAPI
from pydantic import BaseModel

from backend.app.decision_engine import assess_water_risk


app = FastAPI(title="FarmOS API")


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
