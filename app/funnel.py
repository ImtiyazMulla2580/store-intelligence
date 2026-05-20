from sqlalchemy.orm import Session
from app.database import EventDB

def get_funnel(store_id: str, db: Session):
    events = db.query(EventDB).filter(
        EventDB.store_id == store_id,
        EventDB.is_staff == False
    ).all()

    # unique visitors who entered
    entered = set(
        e.visitor_id for e in events if e.event_type == "ENTRY"
    )

    # unique visitors who dwelled in any zone
    browsed = set(
        e.visitor_id for e in events
        if e.event_type == "ZONE_DWELL" and e.visitor_id in entered
    )

    # unique visitors who reached billing zone
    reached_billing = set(
        e.visitor_id for e in events
        if e.zone_id == "BILLING" and e.visitor_id in entered
    )

    # conversion rate
    conversion_rate = (
        round(len(reached_billing) / len(entered) * 100, 2)
        if entered else 0
    )

    return {
        "store_id": store_id,
        "funnel": {
            "entered_store": len(entered),
            "browsed_products": len(browsed),
            "reached_billing": len(reached_billing),
        },
        "conversion_rate_percent": conversion_rate
    }