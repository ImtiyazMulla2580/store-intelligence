# Store Intelligence — Purplle Data Engineer Challenge

A computer vision pipeline that converts raw CCTV footage into
retail analytics metrics.

## What it does
- Detects and tracks visitors in CCTV video using YOLOv8
- Assigns visitors to store zones (Entry, Skincare, Billing etc.)
- Emits structured events (ENTRY, EXIT, ZONE_DWELL, REENTRY)
- Serves metrics via a REST API

## Quick Start

### Run with Python directly
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Run the detection pipeline on a video
```bash
python -m pipeline.run "path/to/video.mp4" STORE_BLR_001 CAM_ENTRY_01
```

### Run tests
```bash
pytest tests/ -v
```

## API Endpoints
| Endpoint | Method | Description |
|---|---|---|
| /health | GET | System status |
| /events/ingest | POST | Ingest events from pipeline |
| /metrics | GET | Visitor counts and dwell times |
| /funnel | GET | Entry to billing conversion funnel |
| /anomalies | GET | Queue buildup and anomaly detection |

Full interactive docs at: http://127.0.0.1:8000/docs

## Tech Stack
- Python 3.12
- FastAPI + SQLAlchemy + SQLite
- YOLOv8 (Ultralytics)
- OpenCV
- Docker

## Design Decisions
See docs/DESIGN.md and docs/CHOICES.md