# AI PROMPT USED: "Write a pipeline runner that takes a video file
# path, runs detection and tracking, then sends all events to an API"

import sys
import time
from pipeline.detect import process_video
from pipeline.tracker import VisitorTracker, get_zone_for_person
from pipeline.emit import send_events, save_to_jsonl

def run_pipeline(video_path, store_id, camera_id):
    print(f"\n{'='*50}")
    print(f"Store:  {store_id}")
    print(f"Camera: {camera_id}")
    print(f"Video:  {video_path}")
    print(f"{'='*50}\n")

    video_start_time = time.time()
    tracker = VisitorTracker()
    all_events = []

    # step 1 - detect persons in video
    detections, fps = process_video(video_path, store_id, camera_id)

    # get frame dimensions from first detection
    frame_width  = 1280  # default
    frame_height = 720

    # step 2 - track and generate events
    for detection in detections:
        timestamp_sec = detection["timestamp_sec"]

        for person in detection["persons"]:
            track_id = person["track_id"]
            bbox     = person["bbox"]
            zone_id  = get_zone_for_person(
                bbox, frame_width, frame_height
            )
            events = tracker.update(track_id, zone_id, timestamp_sec)
            all_events.extend(events)

    # finalize - emit EXIT events for everyone
    if detections:
        final_ts = detections[-1]["timestamp_sec"]
        exit_events = tracker.finalize(final_ts)
        all_events.extend(exit_events)

    print(f"\nTotal events generated: {len(all_events)}")

    # step 3 - send to API and save to file
    send_events(all_events, store_id, camera_id, video_start_time)
    save_to_jsonl(
        all_events, store_id, camera_id,
        video_start_time, "events_output.jsonl"
    )

    print("\n✅ Pipeline complete!")
    return all_events

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python -m pipeline.run <video_path> "
              "<store_id> <camera_id>")
        print("Example: python -m pipeline.run "
              "videos/store1.mp4 STORE_BLR_001 CAM_ENTRY_01")
        sys.exit(1)

    video_path = sys.argv[1]
    store_id   = sys.argv[2]
    camera_id  = sys.argv[3]

    run_pipeline(video_path, store_id, camera_id)