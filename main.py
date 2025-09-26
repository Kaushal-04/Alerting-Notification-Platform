from fastapi import FastAPI, Depends, HTTPException
from database import SessionLocal, engine
import crud
from schemas import AlertCreate, AlertUpdate, AlertOut, DeliveryLog, UserAction, AnalyticsOut
from services.alert_manager import AlertManager
from typing import List
from sqlalchemy.orm import Session
from models import Alert, User
from datetime import date

app = FastAPI(title="Alerting & Notification Platform")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

am = AlertManager()

@app.post("/admin/alerts", response_model=AlertOut)
def admin_create_alert(payload: AlertCreate, db: Session = Depends(get_db)):
    alert = crud.create_alert(db, payload)
    return alert

@app.put("/admin/alerts/{alert_id}", response_model=AlertOut)
def admin_update_alert(alert_id: int, payload: AlertUpdate, db: Session = Depends(get_db)):
    updated = crud.update_alert(db, alert_id, payload.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Alert not found")
    return updated

@app.get("/admin/alerts", response_model=List[AlertOut])
def admin_list_alerts(include_archived: bool = False, db: Session = Depends(get_db)):
    alerts = crud.list_alerts(db, include_archived)
    return alerts

@app.post("/admin/alerts/trigger-reminders", response_model=List[DeliveryLog])
def trigger_reminders(db: Session = Depends(get_db)):
    res = am.trigger_reminders(db)
    return res

@app.get("/user/{user_id}/alerts", response_model=List[AlertOut])
def user_get_alerts(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    alerts = crud.list_active_alerts_for_user(db, user)
    return alerts

@app.post("/user/mark-read")
def user_mark_read(action: UserAction, db: Session = Depends(get_db)):
    pref = crud.mark_read(db, action.user_id, action.alert_id, True)
    return {"status": "ok", "pref_id": pref.id, "read": pref.read}

@app.post("/user/mark-unread")
def user_mark_unread(action: UserAction, db: Session = Depends(get_db)):
    pref = crud.mark_read(db, action.user_id, action.alert_id, False)
    return {"status": "ok", "pref_id": pref.id, "read": pref.read}

@app.post("/user/snooze")
def user_snooze(action: UserAction, db: Session = Depends(get_db)):
    today_str = date.today().isoformat()
    pref = crud.snooze_for_today(db, action.user_id, action.alert_id, today_str)
    return {"status": "ok", "snoozed_until": pref.snoozed_until_date}

@app.get("/analytics", response_model=AnalyticsOut)
def get_analytics(db: Session = Depends(get_db)):
    data = crud.analytics(db)
    return data
