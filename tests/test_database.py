import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base
from backend.app.models import Farm, RiskAssessment, User


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)

    session = Session()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_create_user_and_farm(db_session):
    user = User(
        email="farmer@example.com",
        password_hash="test-hash",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    farm = Farm(
        user_id=user.id,
        name="Demo Farm",
        latitude=-1.2921,
        longitude=36.8219,
        crop="maize",
        growth_stage="vegetative",
    )

    db_session.add(farm)
    db_session.commit()
    db_session.refresh(farm)

    assert farm.id is not None
    assert farm.user_id == user.id
    assert farm.owner.email == "farmer@example.com"


def test_create_risk_assessment_for_farm(db_session):
    user = User(
        email="farmer@example.com",
        password_hash="test-hash",
    )

    farm = Farm(
        owner=user,
        name="Demo Farm",
        latitude=-1.2921,
        longitude=36.8219,
        crop="maize",
        growth_stage="flowering",
    )

    db_session.add(farm)
    db_session.commit()
    db_session.refresh(farm)

    assessment = RiskAssessment(
        farm_id=farm.id,
        recent_rainfall=2.0,
        forecast_rainfall=1.5,
        temperature=35.0,
        risk_level="HIGH",
        score=8,
        confidence="MEDIUM",
        factors="Low recent rainfall, Limited forecast rainfall, High temperature",
        recommendation="Monitor soil moisture closely.",
        explanation=(
            "Water-stress risk increased because of limited rainfall "
            "and high temperature."
        ),
        context="Crop: maize, Growth stage: flowering",
    )

    db_session.add(assessment)
    db_session.commit()
    db_session.refresh(assessment)

    assert assessment.id is not None
    assert assessment.farm_id == farm.id
    assert assessment.farm.name == "Demo Farm"


def test_user_farm_assessment_relationships(db_session):
    user = User(
        email="farmer@example.com",
        password_hash="test-hash",
    )

    farm = Farm(
        owner=user,
        name="Demo Farm",
        latitude=-1.2921,
        longitude=36.8219,
        crop="maize",
        growth_stage="maturity",
    )

    assessment = RiskAssessment(
        farm=farm,
        recent_rainfall=20.0,
        forecast_rainfall=25.0,
        temperature=24.0,
        risk_level="LOW",
        score=0,
        confidence="LOW",
        factors="",
        recommendation="Continue monitoring weather and farm conditions.",
        explanation=(
            "Available conditions do not currently indicate "
            "significant water-stress risk."
        ),
        context="Crop: maize, Growth stage: maturity",
    )

    db_session.add(assessment)
    db_session.commit()

    assert len(user.farms) == 1
    assert user.farms[0] is farm
    assert len(farm.assessments) == 1
    assert farm.assessments[0] is assessment
