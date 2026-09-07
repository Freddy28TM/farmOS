import re

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app import models
from backend.app.database import Base, engine, get_db
from backend.app.decision_engine import assess_water_risk
from backend.app.environmental_data import get_environmental_data
from backend.app.security import (
    create_access_token,
    hash_password,
    verify_access_token,
    verify_password,
)


app = FastAPI(title="FarmOS API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)

security = HTTPBearer()

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class RegistrationRequest(BaseModel):
    email: str
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        value = value.strip().lower()

        if not value:
            raise ValueError("Email cannot be empty")

        if not EMAIL_PATTERN.match(value):
            raise ValueError("Invalid email address")

        return value


class RegistrationResponse(BaseModel):
    id: int
    email: str


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        value = value.strip().lower()

        if not value:
            raise ValueError("Email cannot be empty")

        return value


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class CurrentUserResponse(BaseModel):
    id: int
    email: str


class FarmCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    crop: str
    growth_stage: str = Field(
        ...,
        pattern="^(germination|vegetative|flowering|maturity)$",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Farm name cannot be empty")

        return value

    @field_validator("crop")
    @classmethod
    def validate_crop(cls, value):
        if value != "maize":
            raise ValueError("Crop must be maize")

        return value


class FarmResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    crop: str
    growth_stage: str


class WaterRiskRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    crop: str
    growth_stage: str = Field(
        ...,
        pattern="^(germination|vegetative|flowering|maturity)$",
    )

    @field_validator("crop")
    @classmethod
    def validate_crop(cls, value):
        if value != "maize":
            raise ValueError("Crop must be maize")

        return value


class WaterRiskResponse(BaseModel):
    risk_level: str
    score: int
    confidence: str
    factors: list[str]
    recommendation: str
    explanation: str
    context: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    try:
        user_id = verify_access_token(credentials.credentials)
    except (ValueError, RuntimeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )

    user = db.get(models.User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


@app.get("/")
def root():
    return {"message": "FarmOS API is running"}


@app.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegistrationRequest,
    db: Session = Depends(get_db),
):
    existing_user = db.scalar(
        select(models.User).where(
            models.User.email == request.email
        )
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    user = models.User(
        email=request.email,
        password_hash=hash_password(request.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@app.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(models.User).where(
            models.User.email == request.email
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


@app.get("/me", response_model=CurrentUserResponse)
def get_me(
    current_user: models.User = Depends(get_current_user),
):
    return current_user


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


@app.get("/farms", response_model=list[FarmResponse])
def list_farms(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    farms = db.scalars(
        select(models.Farm)
        .where(models.Farm.user_id == current_user.id)
        .order_by(models.Farm.id)
    ).all()

    return farms


@app.post("/water-risk", response_model=WaterRiskResponse)
def water_risk(
    request: WaterRiskRequest,
):
    try:
        environmental_data = get_environmental_data(
            request.latitude,
            request.longitude,
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
        crop=request.crop,
        growth_stage=request.growth_stage,
    )

    # API-level context combines the farm location with
    # the crop and growth-stage information used by the engine.
    result["context"] = (
        f"Location: ({request.latitude}, {request.longitude}); "
        f"Crop: {request.crop}; "
        f"Growth stage: {request.growth_stage}."
    )

    return result
