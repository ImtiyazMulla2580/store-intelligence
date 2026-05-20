from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.models import Event, EventResponse
from app.database import init_db, get_db, EventDB
from typing import List
from datetime import datetime

app = FastAPI(title="Store Intelligence API")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health(db: Session = Depends(get_db)):
    from sqlalchemy import text
    count = db.execute(text("SELECT COUNT(*) FROM events")).scalar()
    return {
        "status": "ok",
        "message": "API is running",
        "total_events": count
    }

@app.post("/events/ingest")
def ingest_events(events: List[Event], db: Session = Depends(get_db)):
    accepted = 0
    rejected = 0
    errors = []

    for event in events:
        try:
            db_event = EventDB(
                event_id   = event.event_id,
                store_id   = event.store_id,
                camera_id  = event.camera_id,
                visitor_id = event.visitor_id,
                event_type = event.event_type,
                timestamp  = event.timestamp,
                zone_id    = event.zone_id,
                dwell_ms   = event.dwell_ms,
                is_staff   = event.is_staff,
                confidence = event.confidence
            )
            db.add(db_event)
            db.commit()
            accepted += 1
        except Exception as e:
            db.rollback()
            rejected += 1
            errors.append(str(e))

    return EventResponse(accepted=accepted, rejected=rejected, errors=errors)