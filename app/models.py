from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class EventMetadata(BaseModel):
    queue_depth: Optional[int] = None
    sku_zone: Optional[str] = None
    session_seq: int = 1

class Event(BaseModel):
    event_id: str = None
    store_id: str
    camera_id: str
    visitor_id: str
    event_type: str
    timestamp: datetime
    zone_id: Optional[str] = None
    dwell_ms: int = 0
    is_staff: bool = False
    confidence: float = 1.0
    metadata: EventMetadata = EventMetadata()

    def __init__(self, **data):
        super().__init__(**data)
        if not self.event_id:
            self.event_id = str(uuid.uuid4())

class EventResponse(BaseModel):
    accepted: int
    rejected: int
    errors: list = []