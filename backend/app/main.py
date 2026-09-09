import re
from datetime import UTC, datetime

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database import Base, engine, get_db
from backend.app.decision_engine import assess_water_risk
from backend.app.environmental_data import get_environmental_data
from backend.app import models
from backend.app.security import (
    create_access_token,
    hash_password,
    verify_password,
    verify_access_token,
)


app = FastAPI(title="FarmOS API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http" + chr(58) + chr(47) + chr(47) + "localhost:5500",
        "http" + chr(58) + chr(47) + chr(47) + "127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)


security = HTTPBearer()


# ---------------------------------------------------------------------------
# Authentication schemas
# ---------------------------------------------------------------------------

class RegistrationRequest(BaseModel):
    email: str
    password: str = Field(..., min_length=8, max_length=128)


class RegistrationResponse(BaseModel):
    id: int
    email: str


class LoginRequest(BaseModel):
    email: str
    password: str = Field(..., min_length=8, max_length=128)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class CurrentUserResponse(BaseModel):
    id: int
    email: str


# ---------------------------------------------------------------------------
# Farm schemas
# ---------------------------------------------------------------------------

class FarmCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)

    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
    )

    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
    )

    crop: str = Field(
        ...,
        pattern=r"^maize$",
    )

    growth_stage: str = Field(
        ...,
        pattern=r"^(germination|vegetative|flowering|maturity)$",
    )


class FarmResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    crop: str
    growth_stage: str


# ---------------------------------------------------------------------------
# Water-risk schemas
# ---------------------------------------------------------------------------

class WaterRiskRequest(BaseModel):
    farm_id: int = Field(..., gt=0)


class WaterRiskResponse(BaseModel):
    assessment_id: int
    risk_level: str
    score: int
    confidence: str
    factors: list[str]
    recommendation: str
    explanation: str
    context: str


# ---------------------------------------------------------------------------
# Feedback schemas
# ---------------------------------------------------------------------------

class FeedbackRequest(BaseModel):
    farmer_action: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    observed_result: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )


class FeedbackResponse(BaseModel):
    assessment_id: int
    farmer_action: str
    observed_result: str
    feedback_submitted_at: datetime


# ---------------------------------------------------------------------------
# Authentication dependency
# ---------------------------------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        user_id = verify_access_token(token)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        ) from error

    user = db.scalar(
        select(models.User).where(
            models.User.id == user_id
        )
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "FarmOS API is running"
    }


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

@app.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegistrationRequest,
    db: Session = Depends(get_db),
):
    email = request.email.strip().lower()

    if not re.match(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        email,
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid email address",
        )

    existing_user = db.scalar(
        select(models.User).where(
            models.User.email == email
        )
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    user = models.User(
        email=email,
        password_hash=hash_password(request.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "email": user.email,
    }


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

@app.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    email = request.email.strip().lower()

    user = db.scalar(
        select(models.User).where(
            models.User.email == email
        )
    )

    if user is None or not verify_password(
        request.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# ---------------------------------------------------------------------------
# Current user
# ---------------------------------------------------------------------------

@app.get(
    "/me",
    response_model=CurrentUserResponse,
)
def get_me(
    current_user: models.User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "email": current_user.email,
    }


# ---------------------------------------------------------------------------
# Create farm
# ---------------------------------------------------------------------------

@app.post(
    "/farms",
    response_model=FarmResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_farm(
    request: FarmCreateRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    farm = models.Farm(
        user_id=current_user.id,
        name=request.name,
        latitude=request.latitude,
        longitude=request.longitude,
        crop=request.crop,
        growth_stage=request.growth_stage,
    )

    db.add(farm)
    db.commit()
    db.refresh(farm)

    return farm


# ---------------------------------------------------------------------------
# List current user's farms
# ---------------------------------------------------------------------------

@app.get(
    "/farms",
    response_model=list[FarmResponse],
)
def list_farms(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    farms = db.scalars(
        select(models.Farm).where(
            models.Farm.user_id == current_user.id
        )
    ).all()

    return farms


# ---------------------------------------------------------------------------
# Water-risk assessment
# ---------------------------------------------------------------------------

@app.post(
    "/water-risk",
    response_model=WaterRiskResponse,
)
def water_risk(
    request: WaterRiskRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    farm = db.scalar(
        select(models.Farm).where(
            models.Farm.id == request.farm_id,
            models.Farm.user_id == current_user.id,
        )
    )

    if farm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found",
        )

    try:
        environmental_data = get_environmental_data(
            farm.latitude,
            farm.longitude,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error

    result = assess_water_risk(
        recent_rainfall=environmental_data["recent_rainfall"],
        forecast_rainfall=environmental_data["forecast_rainfall"],
        temperature=environmental_data["temperature"],
        crop=farm.crop,
        growth_stage=farm.growth_stage,
    )

    context = (
        f"Location: ({farm.latitude}, {farm.longitude}); "
        f"Crop: {farm.crop}; "
        f"Growth stage: {farm.growth_stage}."
    )

    assessment = models.RiskAssessment(
        farm_id=farm.id,
        recent_rainfall=environmental_data["recent_rainfall"],
        forecast_rainfall=environmental_data["forecast_rainfall"],
        temperature=environmental_data["temperature"],
        risk_level=result["risk_level"],
        score=result["score"],
        confidence=result["confidence"],
        factors=", ".join(result["factors"]),
        recommendation=result["recommendation"],
        explanation=result["explanation"],
        context=context,
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return {
        "assessment_id": assessment.id,
        "risk_level": result["risk_level"],
        "score": result["score"],
        "confidence": result["confidence"],
        "factors": result["factors"],
        "recommendation": result["recommendation"],
        "explanation": result["explanation"],
        "context": context,
    }


# ---------------------------------------------------------------------------
# Submit feedback for a risk assessment
# ---------------------------------------------------------------------------

@app.post(
    "/risk-assessments/{assessment_id}/feedback",
    response_model=FeedbackResponse,
)
def submit_feedback(
    assessment_id: int,
    request: FeedbackRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = db.scalar(
        select(models.RiskAssessment)
        .join(models.Farm)
        .where(
            models.RiskAssessment.id == assessment_id,
            models.Farm.user_id == current_user.id,
        )
    )

    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk assessment not found",
        )

    submitted_at = datetime.now(UTC)

    assessment.farmer_action = request.farmer_action
    assessment.observed_result = request.observed_result
    assessment.feedback_submitted_at = submitted_at

    db.commit()
    db.refresh(assessment)

    return {
        "assessment_id": assessment.id,
        "farmer_action": assessment.farmer_action,
        "observed_result": assessment.observed_result,
        "feedback_submitted_at": assessment.feedback_submitted_at,
    }
