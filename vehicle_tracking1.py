from ultralytics import YOLO

model = YOLO("yolo11n.pt")

video_path = "traffic_video_source2/trafficvideo.mp4"

results = model.track(video_path, persist=True, save=True)

print("TRACKING COMPLETE")