from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Domain(Base):
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    domain_name = Column(String(255), nullable=False)
    spf_status = Column(String(50), default="unknown")
    dkim_status = Column(String(50), default="unknown")
    dmarc_status = Column(String(50), default="unknown")
    overall_ok = Column(Boolean, default=False)
    spf_record = Column(String(1000), nullable=True)
    dkim_record = Column(String(1000), nullable=True)
    dmarc_record = Column(String(1000), nullable=True)
    last_checked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="domains")


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("email_accounts.id"), nullable=False)
    event_type = Column(String(50), nullable=False)  # sent, opened, replied, bounced, spam, clicked
    metadata_json = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    account = relationship("EmailAccount", back_populates="analytics_events")
