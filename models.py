from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
import enum
from database import Base
from datetime import datetime

class Severity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

team_user = Table(
    'team_user',
    Base.metadata,
    Column('team_id', Integer, ForeignKey('teams.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    users = relationship("User", secondary=team_user, back_populates="teams")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    teams = relationship("Team", secondary=team_user, back_populates="users")
    alert_prefs = relationship("UserAlertPreference", back_populates="user")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    message = Column(Text)
    severity = Column(Enum(Severity), default=Severity.INFO)
    delivery = Column(String, default="inapp")
    start_time = Column(DateTime, default=datetime.utcnow)
    expiry_time = Column(DateTime, nullable=True)
    reminder_enabled = Column(Boolean, default=True)
    archived = Column(Boolean, default=False)

    audiences = relationship("AlertAudience", back_populates="alert")
    deliveries = relationship("NotificationDelivery", back_populates="alert")

class AudienceType(str, enum.Enum):
    ORG = "org"
    TEAM = "team"
    USER = "user"

class AlertAudience(Base):
    __tablename__ = "alert_audiences"
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    audience_type = Column(String) 
    audience_id = Column(Integer, nullable=True)
    alert = relationship("Alert", back_populates="audiences")

class NotificationDelivery(Base):
    __tablename__ = "notification_deliveries"
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    delivered_at = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)
    snoozed_for_date = Column(String, nullable=True)
    alert = relationship("Alert", back_populates="deliveries")

class UserAlertPreference(Base):
    __tablename__ = "user_alert_preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    read = Column(Boolean, default=False)
    snoozed_until_date = Column(String, nullable=True)
    user = relationship("User", back_populates="alert_prefs")
