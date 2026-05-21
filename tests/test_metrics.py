# AI PROMPT USED: "Write pytest tests for a FastAPI store analytics
# API that tests the health, ingest, metrics, funnel and anomalies
# endpoints using a test client with an in-memory database"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ── helper ──────────────────────────────────────────────────────────
SAMPLE_EVENTS = [
    {
        "store_id":   "TEST_STORE",
        "camera_id":  "CAM_01",
        "visitor_id": "VIS_001",
        "event_type": "ENTRY",
        "timestamp":  "2026-03-03T10:00:00Z",
        "zone_id":    "ENTRY",
        "dwell_ms":   0,
        "is_staff":   False,
        "confidence": 0.95
    },
    {
        "store_id":   "TEST_STORE",
        "camera_id":  "CAM_01",
        "visitor_id": "VIS_001",
        "event_type": "ZONE_DWELL",
        "timestamp":  "2026-03-03T10:05:00Z",
        "zone_id":    "SKINCARE",
        "dwell_ms":   300000,
        "is_staff":   False,
        "confidence": 0.95
    },
    {
        "store_id":   "TEST_STORE",
        "camera_id":  "CAM_01",
        "visitor_id": "VIS_001",
        "event_type": "EXIT",
        "timestamp":  "2026-03-03T10:10:00Z",
        "zone_id":    "BILLING",
        "dwell_ms":   600000,
        "is_staff":   False,
        "confidence": 0.95
    },
    {
        "store_id":   "TEST_STORE",
        "camera_id":  "CAM_01",
        "visitor_id": "VIS_002",
        "event_type": "ENTRY",
        "timestamp":  "2026-03-03T10:15:00Z",
        "zone_id":    "ENTRY",
        "dwell_ms":   0,
        "is_staff":   False,
        "confidence": 0.90
    }
]

# ── tests ────────────────────────────────────────────────────────────
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_ingest_events():
    response = client.post("/events/ingest", json=SAMPLE_EVENTS)
    assert response.status_code == 200
    data = response.json()
    assert data["accepted"] == 4
    assert data["rejected"] == 0

def test_metrics_returns_data():
    response = client.get("/metrics?store_id=TEST_STORE")
    assert response.status_code == 200
    data = response.json()
    assert data["store_id"] == "TEST_STORE"
    assert data["unique_visitors"] >= 2
    assert data["total_entries"] >= 2

def test_funnel_returns_data():
    response = client.get("/funnel?store_id=TEST_STORE")
    assert response.status_code == 200
    data = response.json()
    assert "funnel" in data
    assert "conversion_rate_percent" in data

def test_anomalies_returns_data():
    response = client.get("/anomalies?store_id=TEST_STORE")
    assert response.status_code == 200
    data = response.json()
    assert "anomalies" in data

def test_ingest_rejects_empty():
    response = client.post("/events/ingest", json=[])
    assert response.status_code == 200
    assert response.json()["accepted"] == 0

def test_metrics_unknown_store():
    response = client.get("/metrics?store_id=UNKNOWN_STORE")
    assert response.status_code == 200
    data = response.json()
    assert data["unique_visitors"] == 0