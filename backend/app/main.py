from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field, field_validator

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.decision_engine import assess_water_risk
from backend.app.environmental_data import get_environmental_data
from backend.app.database import Base, engine, get_db
from backend.app.security import (
    create_access_token,
    hash_password,
    verify_access_token,
    verify_password,
)
from backend.app import models


app = FastAPI(title="FarmOS API")

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    try:
        user_id = verify_access_token(credentials.credentials)
    except (RuntimeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        )

    user = db.scalar(
        select(models.User).where(
            models.User.id == user_id
        )
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        )

    return user




Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RegistrationRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()

        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("Invalid email address")

        if value.count("@") != 1:
            raise ValueError("Invalid email address")

        local_part, domain = value.split("@")

        if not local_part or "." not in domain:
            raise ValueError("Invalid email address")

        if domain.startswith(".") or domain.endswith("."):
            raise ValueError("Invalid email address")

        return value


class RegistrationResponse(BaseModel):
    id: int
    email: str


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()

        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("Invalid email address")

        if value.count("@") != 1:
            raise ValueError("Invalid email address")

        local_part, domain = value.split("@")

        if not local_part or "." not in domain:
            raise ValueError("Invalid email address")

        if domain.startswith(".") or domain.endswith("."):
            raise ValueError("Invalid email address")

        return value


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class CurrentUserResponse(BaseModel):
    id: int
    email: str


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


@app.get("/")
def root():
    return {"message": "FarmOS API is running"}


@app.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=201,
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
            status_code=409,
            detail="Email is already registered",
        )

    user = models.User(
        email=request.email,
        password_hash=hash_password(request.password),
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email is already registered",
        )

    return {
        "id": user.id,
        "email": user.email,
    }


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
            status_code=401,
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
    return {
        "id": current_user.id,
        "email": current_user.email,
    }


@app.post("/water-risk", response_model=WaterRiskResponse)
def water_risk(request: WaterRiskRequest):
    try:
        environmental_data = get_environmental_data(
            latitude=request.latitude,
            longitude=request.longitude,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        )

    result = assess_water_risk(
        recent_rainfall=environmental_data["recent_rainfall"],
        forecast_rainfall=environmental_data["forecast_rainfall"],
        temperature=environmental_data["temperature"],
        crop=request.crop,
        growth_stage=request.growth_stage,
    )

    result["context"] = (
        f"Location: ({request.latitude}, {request.longitude}); "
        f"Crop: {request.crop}; "
        f"Growth stage: {request.growth_stage}."
    )

    return result
