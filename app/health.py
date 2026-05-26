from sqlalchemy.orm import Session
from sqlalchemy import text

def get_health(db: Session):
    count = db.execute(
        text("SELECT COUNT(*) FROM events")
    ).scalar()
    return {
        "status": "ok",
        "message": "API is running",
        "total_events": count
    }