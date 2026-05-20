# AI PROMPT USED: "Write a zone detector that checks if a person's
# bounding box centroid falls inside a defined zone rectangle,
# and tracks entry/exit/dwell events per visitor"

def get_centroid(bbox):
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)

def get_zones(frame_width, frame_height):
    """
    Divide the frame into zones based on position.
    Left = ENTRY, Middle = FLOOR, Right = BILLING
    """
    w, h = frame_width, frame_height
    return {
        "ENTRY":   (0,       0, w*0.25, h),
        "SKINCARE":(w*0.25,  0, w*0.5,  h*0.5),
        "MAKEUP":  (w*0.25,  h*0.5, w*0.5, h),
        "HAIRCARE":(w*0.5,   0, w*0.75, h*0.5),
        "BILLING": (w*0.75,  0, w,      h),
    }

def point_in_zone(cx, cy, zone_rect):
    x1, y1, x2, y2 = zone_rect
    return x1 <= cx <= x2 and y1 <= cy <= y2

def get_zone_for_person(bbox, frame_width, frame_height):
    cx, cy = get_centroid(bbox)
    zones = get_zones(frame_width, frame_height)
    for zone_id, rect in zones.items():
        if point_in_zone(cx, cy, rect):
            return zone_id
    return None

class VisitorTracker:
    def __init__(self):
        self.visitors = {}  # track_id -> state

    def update(self, track_id, zone_id, timestamp_sec):
        """
        Update visitor state and return event if something happened.
        """
        events = []
        visitor_key = str(track_id)

        if visitor_key not in self.visitors:
            # first time seeing this person
            self.visitors[visitor_key] = {
                "zone": zone_id,
                "entry_time": timestamp_sec,
                "last_seen": timestamp_sec,
                "exited": False,
                "entry_count": 1
            }
            events.append({
                "event_type": "ENTRY",
                "visitor_id": f"VIS_{visitor_key}",
                "zone_id": zone_id,
                "timestamp_sec": timestamp_sec,
                "dwell_ms": 0
            })
        else:
            state = self.visitors[visitor_key]
            prev_zone = state["zone"]
            state["last_seen"] = timestamp_sec

            if state["exited"] and zone_id == "ENTRY":
                # person came back - REENTRY
                state["exited"] = False
                state["entry_count"] += 1
                events.append({
                    "event_type": "REENTRY",
                    "visitor_id": f"VIS_{visitor_key}",
                    "zone_id": zone_id,
                    "timestamp_sec": timestamp_sec,
                    "dwell_ms": 0
                })

            elif prev_zone != zone_id and zone_id is not None:
                # person moved to new zone
                dwell_ms = int((timestamp_sec - state["entry_time"]) * 1000)
                events.append({
                    "event_type": "ZONE_DWELL",
                    "visitor_id": f"VIS_{visitor_key}",
                    "zone_id": prev_zone,
                    "timestamp_sec": timestamp_sec,
                    "dwell_ms": dwell_ms
                })
                state["zone"] = zone_id
                state["entry_time"] = timestamp_sec

        return events

    def finalize(self, timestamp_sec):
        """
        At end of video, emit EXIT for everyone still in store.
        """
        events = []
        for visitor_key, state in self.visitors.items():
            if not state["exited"]:
                dwell_ms = int(
                    (timestamp_sec - state["entry_time"]) * 1000
                )
                events.append({
                    "event_type": "EXIT",
                    "visitor_id": f"VIS_{visitor_key}",
                    "zone_id": state["zone"],
                    "timestamp_sec": timestamp_sec,
                    "dwell_ms": dwell_ms
                })
                state["exited"] = True
        return events