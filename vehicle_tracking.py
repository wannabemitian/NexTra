from ultralytics import YOLO
import pandas as pd

model = YOLO("yolo11n.pt")

video_path = "traffic_video_source2/trafficvideo.mp4"

results = model.track(video_path, persist=True)

rows = []

for frame_number, result in enumerate(results):

    if result.boxes.id is not None:

        ids = result.boxes.id.tolist()
        boxes = result.boxes.xyxy.tolist()

        for vehicle_id, box in zip(ids, boxes):

            x1, y1, x2, y2 = box

            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            rows.append({
                "frame": frame_number,
                "vehicle_id": int(vehicle_id),
                "center_x": round(center_x),
                "center_y": round(center_y)
            })

df = pd.DataFrame(rows)

df.to_csv("vehicle_tracking_data.csv", index=False)

print("CSV SAVED")
print(df.head())
df = pd.DataFrame(rows)
df.to_csv("vehicle_tracking_data.csv", index=False)
df.to_csv("vehicle_tracking_data.csv", index=False)