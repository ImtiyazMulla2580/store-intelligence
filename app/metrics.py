from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import EventDB
from datetime import datetime

def get_metrics(store_id: str, db: Session, date: str = None):
    query = db.query(EventDB).filter(
        EventDB.store_id == store_id,
        EventDB.is_staff == False
    )

    if date:
        day = datetime.strptime(date, "%Y-%m-%d")
        query = query.filter(
            func.date(EventDB.timestamp) == day.date()
        )

    all_events = query.all()

    # unique visitors (unique visitor_ids)
    unique_visitors = len(set(e.visitor_id for e in all_events))

    # entries and exits
    entries = [e for e in all_events if e.event_type == "ENTRY"]
    exits   = [e for e in all_events if e.event_type == "EXIT"]

    # reentries
    reentries = [e for e in all_events if e.event_type == "REENTRY"]

    # average dwell time (only EXIT events have dwell_ms)
    dwell_times = [e.dwell_ms for e in exits if e.dwell_ms > 0]
    avg_dwell_ms = sum(dwell_times) / len(dwell_times) if dwell_times else 0

    # zone breakdown
    zone_events = [e for e in all_events if e.zone_id and e.event_type == "ZONE_DWELL"]
    zone_summary = {}
    for e in zone_events:
        if e.zone_id not in zone_summary:
            zone_summary[e.zone_id] = {"visits": 0, "total_dwell_ms": 0}
        zone_summary[e.zone_id]["visits"] += 1
        zone_summary[e.zone_id]["total_dwell_ms"] += e.dwell_ms

    return {
        "store_id": store_id,
        "date": date or "all",
        "unique_visitors": unique_visitors,
        "total_entries": len(entries),
        "total_exits": len(exits),
        "total_reentries": len(reentries),
        "avg_dwell_seconds": round(avg_dwell_ms / 1000, 2),
        "zone_summary": zone_summary
    }