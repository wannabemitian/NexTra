import pandas as pd
from ultralytics import YOLO


def analyze_camera(video_path, camera_name, model, vehicle_classes=(2, 3, 5, 7)):
    """
    Analyze one traffic camera video.

    Returns a DataFrame containing:
    - camera
    - frame
    - vehicle_id
    - center_x
    - center_y
    """

    results = model.track(
        video_path,
        persist=True,
        stream=True,
        verbose=False,
        classes=list(vehicle_classes)
    )

    rows = []

    for frame_number, result in enumerate(results):

        if result.boxes.id is None:
            continue

        ids = result.boxes.id.tolist()
        boxes = result.boxes.xyxy.tolist()

        for vehicle_id, box in zip(ids, boxes):

            x1, y1, x2, y2 = box

            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            rows.append({
                "camera": camera_name,
                "frame": frame_number,
                "vehicle_id": int(vehicle_id),
                "center_x": round(center_x),
                "center_y": round(center_y)
            })

    return pd.DataFrame(rows)


print("camera_analysis.py started")


if __name__ == "__main__":
    cameras = {
        "Camera_A": "traffic_video_source2/trafficvideo.mp4",
        "Camera_B": "camera_B.mp4"
    }

    for camera_name, video_path in cameras.items():

        print(f"\nAnalyzing {camera_name}: {video_path}")

        model = YOLO("yolo11n.pt")

        data = analyze_camera(
            video_path,
            camera_name,
            model
        )

        output_file = f"{camera_name}_tracking.csv"
        data.to_csv(output_file, index=False)

        print(f"Saved: {output_file}")

        if data.empty:
            print("Vehicles observed: 0")
            print("WARNING: No vehicles detected.")
        else:
            print(f"Vehicles observed: {data['vehicle_id'].nunique()}")