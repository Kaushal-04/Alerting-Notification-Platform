from crud import list_users, list_teams, list_alerts, create_delivery_log, list_active_alerts_for_user, create_alert, update_alert
from database import SessionLocal
from models import Alert, User
from services.delivery import DeliveryContext, InAppDelivery
from datetime import datetime, date
from typing import List

class AlertManager:
    def __init__(self):
        self.delivery_context = DeliveryContext(InAppDelivery())

    def resolve_audience_users(self, db, alert: Alert) -> List[User]:
        users = []
        audiences = alert.audiences
        all_users = db.query(User).all()
        for aud in audiences:
            if aud.audience_type == "org":
                users = all_users
                break
            if aud.audience_type == "team" and aud.audience_id:
                for u in all_users:
                    for t in u.teams:
                        if t.id == aud.audience_id:
                            users.append(u)
            if aud.audience_type == "user" and aud.audience_id:
                u = db.query(User).filter(User.id == aud.audience_id).first()
                if u:
                    users.append(u)
        return list({u.id:u for u in users}.values())

    def trigger_reminders(self, db):
        now = datetime.utcnow()
        alerts = db.query(Alert).filter(Alert.archived == False).filter(Alert.reminder_enabled == True).all()
        results = []
        for a in alerts:
            if a.start_time and a.start_time > now:
                continue
            if a.expiry_time and a.expiry_time < now:
                continue
            users = self.resolve_audience_users(db, a)
            send_to = []
            for u in users:
                pref = db.query(User).filter(User.id==u.id).first()
                # check user-specific snooze
                from crud import get_or_create_user_pref
                up = get_or_create_user_pref(db, u.id, a.id)
                today_str = date.today().isoformat()
                if up.snoozed_until_date == today_str:
                    continue
                send_to.append(u)
            if send_to:
                res = self.delivery_context.send(a, send_to)
                results.extend(res)
        return results
