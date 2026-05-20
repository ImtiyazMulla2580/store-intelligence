# AI PROMPT USED: "Write a YOLOv8 people detector that reads a video
# file frame by frame, detects only persons (class 0), and returns
# bounding boxes with confidence scores for each frame"

import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")  # downloads automatically first time

def detect_persons(frame):
    """
    Takes a video frame, returns list of detected persons.
    Each person = {bbox, confidence, track_id}
    """
    results = model.track(frame, persist=True, classes=[0], verbose=False)
    persons = []

    if results[0].boxes is not None:
        for box in results[0].boxes:
            if box.id is not None:
                persons.append({
                    "track_id": int(box.id.item()),
                    "confidence": float(box.conf.item()),
                    "bbox": box.xyxy[0].tolist()
                })

    return persons

def process_video(video_path: str, store_id: str, camera_id: str):
    """
    Reads a video file and detects persons in each frame.
    Returns list of detections per frame.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Processing: {video_path}")
    print(f"FPS: {fps}, Total frames: {total_frames}")

    detections = []
    frame_num = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # process every 5th frame to save time
        if frame_num % 5 == 0:
            persons = detect_persons(frame)
            timestamp_sec = frame_num / fps
            detections.append({
                "frame": frame_num,
                "timestamp_sec": round(timestamp_sec, 2),
                "persons": persons
            })

            # print progress every 100 frames
            if frame_num % 100 == 0:
                print(f"Frame {frame_num}/{total_frames} — "
                      f"{len(persons)} persons detected")

        frame_num += 1

    cap.release()
    print(f"Done! Processed {frame_num} frames.")
    return detections, fps