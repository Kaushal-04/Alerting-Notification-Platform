# Alerting & Notification Platform - MVP (Backend)

## Overview
FastAPI-based backend implementing:
- Admin APIs: create/update/list alerts
- User APIs: fetch alerts, mark read/unread, snooze
- Analytics endpoint
- Reminder trigger endpoint (simulate 2-hour reminders)
- In-app delivery (MVP) using delivery strategy pattern
- SQLite + SQLAlchemy

## Setup
1. python -m venv venv
2. source venv/bin/activate (or venv\Scripts\activate on Windows)
3. pip install -r requirements.txt
4. Run seed to create DB data:
   `python seed.py`
5. Start server:
   `uvicorn main:app --reload --port 8000`
6. API docs:
   `http://127.0.0.1:8000/docs`

## Notes
- To simulate reminders, call the POST /admin/alerts/trigger-reminders endpoint.
- Snooze is per day; snooze expires at midnight server date.
- Reminder frequency default is 2 hours; reminders are simulated (no background scheduler) to keep the MVP simple and testable.
