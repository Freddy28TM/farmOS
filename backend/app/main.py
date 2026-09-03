from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field

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
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    crop: str
    growth_stage: str


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
        crop=request.crop,
        growth_stage=request.growth_stage,
    )
