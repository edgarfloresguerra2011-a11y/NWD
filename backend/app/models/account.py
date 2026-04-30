from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class EmailAccount(Base):
    __tablename__ = "email_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email = Column(String(255), nullable=False)
    provider = Column(String(50), nullable=False)
    status = Column(String(50), default="connecting")

    # Auth
    access_token = Column(String(1000), nullable=True)
    refresh_token = Column(String(1000), nullable=True)
    smtp_host = Column(String(255), nullable=True)
    smtp_port = Column(Integer, nullable=True)
    imap_host = Column(String(255), nullable=True)
    imap_port = Column(Integer, nullable=True)
    smtp_username = Column(String(255), nullable=True)
    smtp_password = Column(String(500), nullable=True)

    # Warmup metrics
    warmup_progress = Column(Float, default=0.0)
    reputation_score = Column(Float, default=50.0)
    emails_sent_today = Column(Integer, default=0)
    emails_received_today = Column(Integer, default=0)
    opens_today = Column(Integer, default=0)
    replies_today = Column(Integer, default=0)
    bounce_rate = Column(Float, default=0.0)
    spam_rate = Column(Float, default=0.0)

    # DNS
    spf_ok = Column(Boolean, default=False)
    dkim_ok = Column(Boolean, default=False)
    dmarc_ok = Column(Boolean, default=False)

    # Warmup config
    warmup_max_per_day = Column(Integer, default=50)
    warmup_reply_rate = Column(Float, default=0.05)
    warmup_ramp_days = Column(Integer, default=28)

    warmup_day = Column(Integer, default=1)
    last_warmup_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="accounts")
    analytics_events = relationship("AnalyticsEvent", back_populates="account", cascade="all, delete-orphan")
    warmup_logs = relationship("WarmupLog", back_populates="account", cascade="all, delete-orphan")


class WarmupPool(Base):
    __tablename__ = "warmup_pool"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    category = Column(String(50), default="global")  # global, private, test
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class WarmupLog(Base):
    __tablename__ = "warmup_logs"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("email_accounts.id"), nullable=False)
    to_email = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=True)
    action = Column(String(50), nullable=False)  # sent, received, open, reply, bounce, spam
    status = Column(String(50), default="success")
    message_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    account = relationship("EmailAccount", back_populates="warmup_logs")
