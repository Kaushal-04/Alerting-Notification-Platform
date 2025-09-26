from database import Base, engine, SessionLocal
from models import Team, User, Alert, AlertAudience
from datetime import datetime, timedelta
from crud import create_alert
import schemas

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()
t1 = Team(name="Engineering")
t2 = Team(name="Marketing")
db.add_all([t1,t2])
db.commit()
db.refresh(t1)
db.refresh(t2)

u1 = User(name="Alice", email="alice@example.com")
u1.teams.append(t1)
u2 = User(name="Bob", email="bob@example.com")
u2.teams.append(t2)
u3 = User(name="Charlie", email="charlie@example.com")
u3.teams.append(t1)
db.add_all([u1,u2,u3])
db.commit()

now = datetime.utcnow()
a1 = schemas.AlertCreate(
    title="Database maintenance",
    message="We will have DB maintenance in 1 hour.",
    severity="warning",
    delivery="inapp",
    start_time=now - timedelta(hours=1),
    expiry_time=now + timedelta(days=1),
    audiences=[schemas.Audience(type="team", id=t1.id)]
)
a2 = schemas.AlertCreate(
    title="All hands meeting",
    message="Company wide meeting at 5pm.",
    severity="info",
    delivery="inapp",
    start_time=now - timedelta(hours=2),
    expiry_time=now + timedelta(days=2),
    audiences=[schemas.Audience(type="org", id=None)]
)
create_alert(db, a1)
create_alert(db, a2)
db.close()
print("Seeded DB with teams, users and 2 alerts")
