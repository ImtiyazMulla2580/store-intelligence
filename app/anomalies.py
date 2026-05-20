from sqlalchemy.orm import Session
from app.database import EventDB
from datetime import timedelta

def get_anomalies(store_id: str, db: Session):
    events = db.query(EventDB).filter(
        EventDB.store_id == store_id,
        EventDB.is_staff == False
    ).order_by(EventDB.timestamp).all()

    anomalies = []

    # anomaly 1 - queue buildup (5+ people in billing at same time)
    billing_events = [e for e in events if e.zone_id == "BILLING"]
    if len(billing_events) >= 5:
        anomalies.append({
            "type": "QUEUE_BUILDUP",
            "description": "5 or more visitors in billing zone",
            "count": len(billing_events)
        })

    # anomaly 2 - very long dwell time (over 30 minutes)
    long_dwell = [
        e for e in events
        if e.dwell_ms > 30 * 60 * 1000
    ]
    if long_dwell:
        anomalies.append({
            "type": "LONG_DWELL",
            "description": "Visitor dwelled for over 30 minutes",
            "count": len(long_dwell)
        })

    # anomaly 3 - reentry spike (same visitor entering 3+ times)
    from collections import Counter
    reentries = [e for e in events if e.event_type == "REENTRY"]
    reentry_counts = Counter(e.visitor_id for e in reentries)
    frequent_reentries = {
        vid: cnt for vid, cnt in reentry_counts.items() if cnt >= 3
    }
    if frequent_reentries:
        anomalies.append({
            "type": "FREQUENT_REENTRY",
            "description": "Visitor re-entered store 3 or more times",
            "count": len(frequent_reentries)
        })

    return {
        "store_id": store_id,
        "anomalies_found": len(anomalies),
        "anomalies": anomalies
    }