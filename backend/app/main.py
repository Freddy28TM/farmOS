from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from backend.app.decision_engine import assess_water_risk
from backend.app.environmental_data import get_environmental_data


app = FastAPI(title="FarmOS API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class WaterRiskRequest(BaseModel):
    latitude: float
    longitude: float


@app.get("/")
def root():
    return {"message": "FarmOS API is running"}


@app.post("/water-risk")
def water_risk(request: WaterRiskRequest):
    environmental_data = get_environmental_data(
        latitude=request.latitude,
        longitude=request.longitude,
    )

    return assess_water_risk(
        recent_rainfall=environmental_data["recent_rainfall"],
        forecast_rainfall=environmental_data["forecast_rainfall"],
        temperature=environmental_data["temperature"],
    )