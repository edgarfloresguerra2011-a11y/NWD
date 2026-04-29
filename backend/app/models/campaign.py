from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="draft")

    # Metrics
    total_emails = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    open_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    bounce_count = Column(Integer, default=0)
    spam_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="campaigns")
    steps = relationship("CampaignStep", back_populates="campaign", cascade="all, delete-orphan", order_by="CampaignStep.step_order")

    @property
    def open_rate(self):
        if self.sent_count == 0:
            return 0.0
        return round((self.open_count / self.sent_count) * 100, 1)

    @property
    def reply_rate(self):
        if self.sent_count == 0:
            return 0.0
        return round((self.reply_count / self.sent_count) * 100, 1)


class CampaignStep(Base):
    __tablename__ = "campaign_steps"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    step_order = Column(Integer, nullable=False)
    action = Column(String(50), default="send_email")
    subject = Column(String(500), nullable=True)
    body_text = Column(Text, nullable=True)
    delay_hours = Column(Integer, default=24)
    condition_field = Column(String(100), nullable=True)
    condition_value = Column(String(100), nullable=True)

    campaign = relationship("Campaign", back_populates="steps")
