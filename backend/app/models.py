from datetime import datetime, UTC

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    farms: Mapped[list["Farm"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )


class Farm(Base):
    __tablename__ = "farms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    crop: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    growth_stage: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    owner: Mapped["User"] = relationship(
        back_populates="farms",
    )

    assessments: Mapped[list["RiskAssessment"]] = relationship(
        back_populates="farm",
        cascade="all, delete-orphan",
    )


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(
        ForeignKey("farms.id"),
        nullable=False,
        index=True,
    )

    recent_rainfall: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    forecast_rainfall: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    temperature: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    risk_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    confidence: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    factors: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    recommendation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    context: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    farm: Mapped["Farm"] = relationship(
        back_populates="assessments",
    )
