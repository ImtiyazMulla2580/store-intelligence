from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from app.models import Event, EventResponse
from app.database import init_db, get_db, EventDB
from app.metrics import get_metrics
from app.funnel import get_funnel
from app.anomalies import get_anomalies
from typing import List, Optional

app = FastAPI(title="Store Intelligence API")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health(db: Session = Depends(get_db)):
    from sqlalchemy import text
    count = db.execute(text("SELECT COUNT(*) FROM events")).scalar()
    return {"status": "ok", "message": "API is running", "total_events": count}

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

@app.get("/metrics")
def metrics(
    store_id: str,
    date: Optional[str] = Query(None, description="Format: YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    return get_metrics(store_id, db, date)

@app.get("/funnel")
def funnel(store_id: str, db: Session = Depends(get_db)):
    return get_funnel(store_id, db)

@app.get("/anomalies")
def anomalies(store_id: str, db: Session = Depends(get_db)):
    return get_anomalies(store_id, db)