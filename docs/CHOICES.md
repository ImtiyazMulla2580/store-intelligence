# Technical Choices & Tradeoffs

## 1. YOLOv8n for Person Detection
**Chose:** YOLOv8n (nano variant)
**Why:** Fastest inference speed, sufficient accuracy for retail
density. Pretrained on COCO dataset which includes "person" class.
**Tradeoff:** Larger YOLOv8m would be more accurate but 5x slower.
For a 48-hour challenge, speed of iteration matters more.

## 2. Built-in YOLO Tracker instead of separate ByteTrack
**Chose:** YOLO's persist=True tracking
**Why:** Zero extra dependencies, works out of the box, gives
consistent track_id per person across frames.
**Tradeoff:** A dedicated ByteTrack implementation handles occlusion
better but requires significant extra code.

## 3. SQLite instead of PostgreSQL
**Chose:** SQLite via SQLAlchemy
**Why:** No setup required, works inside Docker with a volume mount,
sufficient for the data volumes in this challenge.
**Tradeoff:** Not suitable for concurrent writes at scale. In
production I would use PostgreSQL with connection pooling.

## 4. FastAPI instead of Flask/Django
**Chose:** FastAPI
**Why:** Automatic OpenAPI docs (/docs), built-in Pydantic validation,
async support, and modern Python type hints. The auto-generated docs
page makes it easy for evaluators to test endpoints interactively.
**Tradeoff:** Slightly steeper learning curve than Flask for beginners.

## 5. Zone detection by centroid position
**Chose:** Divide frame into fixed rectangular zones by position
**Why:** Simple, deterministic, requires no extra training data.
Works well when camera angles are consistent.
**Tradeoff:** A homography-based approach using store_layout.json
coordinates would be more accurate but requires camera calibration.

## 6. Process every 5th frame
**Chose:** Sample 1 in every 5 frames (at 30fps = 6 samples/sec)
**Why:** Reduces processing time by 80% with minimal accuracy loss.
Human movement at walking pace changes little between frames.
**Tradeoff:** Fast movements or quick zone transitions could be missed.

## 7. AI Tools Used
- Claude (Anthropic) — used for code generation, debugging, and
  documentation. All prompts are documented as comments at the top
  of each relevant file.
- YOLOv8 (Ultralytics) — pretrained model, not fine-tuned.

## 8. What I would do with more time
- Fine-tune YOLO on retail store footage for better accuracy
- Add Re-ID model (OSNet) for cross-camera visitor tracking
- Replace SQLite with PostgreSQL
- Add Prometheus metrics and Grafana dashboard
- Add staff detection by uniform colour classification