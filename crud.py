from sqlalchemy.orm import Session
from models import User, Team, Alert, AlertAudience, AudienceType, NotificationDelivery, UserAlertPreference, Severity
from datetime import datetime
from typing import List
from schemas import AlertCreate

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def list_users(db: Session):
    return db.query(User).all()

def list_teams(db: Session):
    return db.query(Team).all()

def create_alert(db: Session, payload: AlertCreate):
    alert = Alert(
        title=payload.title,
        message=payload.message,
        severity=payload.severity,
        delivery=payload.delivery,
        start_time=payload.start_time or datetime.utcnow(),
        expiry_time=payload.expiry_time,
        reminder_enabled=payload.reminder_enabled,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    for aud in payload.audiences:
        a = AlertAudience(alert_id=alert.id, audience_type=aud.type, audience_id=aud.id)
        db.add(a)
    db.commit()
    db.refresh(alert)
    return alert

def update_alert(db: Session, alert_id: int, data: dict):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return None
    for k, v in data.items():
        if hasattr(alert, k) and v is not None:
            setattr(alert, k, v)
    db.commit()
    db.refresh(alert)
    return alert

def list_alerts(db: Session, include_archived=False):
    q = db.query(Alert)
    if not include_archived:
        q = q.filter(Alert.archived == False)
    return q.all()

def get_alert(db: Session, alert_id: int):
    return db.query(Alert).filter(Alert.id == alert_id).first()

def deliveries_for_alert(db: Session, alert_id: int):
    return db.query(NotificationDelivery).filter(NotificationDelivery.alert_id == alert_id).all()

def create_delivery_log(db: Session, alert_id: int, user_id: int):
    nd = NotificationDelivery(alert_id=alert_id, user_id=user_id)
    db.add(nd)
    db.commit()
    db.refresh(nd)
    return nd

def get_or_create_user_pref(db: Session, user_id:int, alert_id:int):
    pref = db.query(UserAlertPreference).filter(UserAlertPreference.user_id==user_id, UserAlertPreference.alert_id==alert_id).first()
    if pref:
        return pref
    pref = UserAlertPreference(user_id=user_id, alert_id=alert_id)
    db.add(pref)
    db.commit()
    db.refresh(pref)
    return pref

def mark_read(db: Session, user_id:int, alert_id:int, read:bool):
    pref = get_or_create_user_pref(db, user_id, alert_id)
    pref.read = read
    db.commit()
    db.refresh(pref)
    return pref

def snooze_for_today(db: Session, user_id:int, alert_id:int, date_str:str):
    pref = get_or_create_user_pref(db, user_id, alert_id)
    pref.snoozed_until_date = date_str
    db.commit()
    db.refresh(pref)
    return pref

def list_active_alerts_for_user(db: Session, user:User):
    now = datetime.utcnow()
    alerts = db.query(Alert).filter(Alert.archived == False).filter((Alert.start_time <= now)).filter((Alert.expiry_time == None) | (Alert.expiry_time >= now)).all()
    res = []
    for a in alerts:
        audiences = a.audiences
        for aud in audiences:
            if aud.audience_type == "org":
                res.append(a)
                break
            if aud.audience_type == "team" and aud.audience_id:
                for t in user.teams:
                    if t.id == aud.audience_id:
                        res.append(a)
                        break
            if aud.audience_type == "user" and aud.audience_id == user.id:
                res.append(a)
                break
    return list({a.id: a for a in res}.values())

def analytics(db: Session):
    total_alerts = db.query(Alert).count()
    delivered_count = db.query(NotificationDelivery).count()
    read_count = db.query(NotificationDelivery).filter(NotificationDelivery.read == True).count()
    snoozed = db.query(NotificationDelivery).filter(NotificationDelivery.snoozed_for_date != None).all()
    snoozed_counts = {}
    for s in snoozed:
        snoozed_counts.setdefault(s.alert_id, 0)
        snoozed_counts[s.alert_id] += 1
    by_sev = {}
    for sev in [Severity.INFO, Severity.WARNING, Severity.CRITICAL]:
        by_sev[sev.value] = db.query(Alert).filter(Alert.severity == sev).count()
    return {
        "total_alerts": total_alerts,
        "delivered_count": delivered_count,
        "read_count": read_count,
        "snoozed_counts": snoozed_counts,
        "by_severity": by_sev
    }
