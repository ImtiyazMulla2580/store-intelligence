# AI PROMPT USED: "Write a function that converts raw tracker events
# into structured JSONL format and sends them to a FastAPI endpoint
# via HTTP POST"

import httpx
import json
from datetime import datetime, timezone

API_URL = "http://127.0.0.1:8000/events/ingest"

def build_event(raw_event, store_id, camera_id, video_start_time):
    """Convert raw tracker event to API event format."""
    ts = video_start_time + raw_event["timestamp_sec"]
    dt = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()

    return {
        "store_id":   store_id,
        "camera_id":  camera_id,
        "visitor_id": raw_event["visitor_id"],
        "event_type": raw_event["event_type"],
        "timestamp":  dt,
        "zone_id":    raw_event.get("zone_id"),
        "dwell_ms":   raw_event.get("dwell_ms", 0),
        "is_staff":   False,
        "confidence": 0.85
    }

def send_events(events_batch, store_id, camera_id, video_start_time):
    """Send a batch of events to the API."""
    if not events_batch:
        return

    payload = [
        build_event(e, store_id, camera_id, video_start_time)
        for e in events_batch
    ]

    try:
        response = httpx.post(API_URL, json=payload, timeout=30)
        result = response.json()
        print(f"Sent {len(payload)} events → "
              f"accepted: {result['accepted']}, "
              f"rejected: {result['rejected']}")
    except Exception as e:
        print(f"Failed to send events: {e}")

def save_to_jsonl(events_batch, store_id, camera_id,
                  video_start_time, output_path):
    """Also save events to a .jsonl file for records."""
    with open(output_path, "a") as f:
        for e in events_batch:
            event = build_event(e, store_id, camera_id, video_start_time)
            f.write(json.dumps(event) + "\n")