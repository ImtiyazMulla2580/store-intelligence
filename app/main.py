from fastapi import FastAPI
from app.models import Event, EventResponse
from typing import List

app = FastAPI(title="Store Intelligence API")

# temporary in-memory storage
events_db = []

@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "API is running",
        "total_events": len(events_db)
    }

@app.post("/events/ingest")
def ingest_events(events: List[Event]):
    accepted = 0
    rejected = 0
    errors = []

    for event in events:
        try:
            events_db.append(event.dict())
            accepted += 1
        except Exception as e:
            rejected += 1
            errors.append(str(e))

    return EventResponse(accepted=accepted, rejected=rejected, errors=errors)