from sqlalchemy.orm import Session
from app.models import Event, EventResponse
from app.database import EventDB

def ingest_events(events, db: Session):
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

    return EventResponse(
        accepted=accepted,
        rejected=rejected,
        errors=errors
    )