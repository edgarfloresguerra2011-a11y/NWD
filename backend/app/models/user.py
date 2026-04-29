from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class PlanTier(str, enum.Enum):
    STARTER = "starter"
    GROWTH = "growth"
    AGENCY = "agency"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    company = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    plan_tier = Column(String(50), default=PlanTier.STARTER.value)
    whitelabel_enabled = Column(Boolean, default=False)
    whitelabel_domain = Column(String(255), nullable=True)
    whitelabel_logo_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    accounts = relationship("EmailAccount", back_populates="user", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="user", cascade="all, delete-orphan")
    domains = relationship("Domain", back_populates="user", cascade="all, delete-orphan")
