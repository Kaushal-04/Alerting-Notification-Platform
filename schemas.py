from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from models import Severity

class Audience(BaseModel):
    type: str
    id: Optional[int] = None

class AlertCreate(BaseModel):
    title: str
    message: str
    severity: Severity = Severity.INFO
    delivery: str = "inapp"
    start_time: Optional[datetime] = None
    expiry_time: Optional[datetime] = None
    reminder_enabled: bool = True
    audiences: List[Audience] = []

class AlertUpdate(BaseModel):
    title: Optional[str]
    message: Optional[str]
    severity: Optional[Severity]
    delivery: Optional[str]
    start_time: Optional[datetime]
    expiry_time: Optional[datetime]
    reminder_enabled: Optional[bool]
    archived: Optional[bool]

class AlertOut(BaseModel):
    id: int
    title: str
    message: str
    severity: Severity
    delivery: str
    start_time: Optional[datetime]
    expiry_time: Optional[datetime]
    reminder_enabled: bool
    archived: bool

    class Config:
        orm_mode = True

class DeliveryLog(BaseModel):
    id: int
    alert_id: int
    user_id: int
    delivered_at: datetime
    read: bool
    snoozed_for_date: Optional[str]

    class Config:
        orm_mode = True

class UserAction(BaseModel):
    user_id: int
    alert_id: int

class AnalyticsOut(BaseModel):
    total_alerts: int
    delivered_count: int
    read_count: int
    snoozed_counts: dict
    by_severity: dict
