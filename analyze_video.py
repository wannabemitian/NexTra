from pathlib import Path
import subprocess


import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO

FFMPEG_PATH = r"C:\Users\Jyothipavan\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build-shared\bin\ffmpeg.exe"

# Load the pretrained vehicle-detection model
model = YOLO("yolo11n.pt")


def analyze_video(video_path):
    """
    Analyze a traffic video and create an annotated output video.

    Input:
        video_path - path to the uploaded traffic video

    Output:
        Dictionary containing traffic statistics and the
        path to the annotated video.
    """

    video_path = Path(video_path)

    rows = []

    # ---------------------------------------------------------
    # 1. OPEN INPUT VIDEO
    # ---------------------------------------------------------

    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if fps <= 0:
        fps = 30

    # Create an output filename beside the uploaded video
    output_path = (
        video_path.parent /
        f"{video_path.stem}_annotated.mp4"
    )

    h264_output_path = (
    video_path.parent /
    f"{video_path.stem}_annotated_h264.mp4"
    )

    # ---------------------------------------------------------
    # 2. CREATE OUTPUT VIDEO WRITER
    # ---------------------------------------------------------

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    writer = cv2.VideoWriter(
        str(output_path),
        fourcc,
        fps,
        (width, height)
    )

    if not writer.isOpened():
        cap.release()
        raise ValueError(
            f"Could not create output video: {output_path}"
        )

    cap.release()

    # ---------------------------------------------------------
    # 3. RUN YOLO TRACKING
    # ---------------------------------------------------------

    results = model.track(
        source=str(video_path),
        persist=True,
        stream=True,
        verbose=False,
        classes=[2, 3, 5, 7]
    )

    # ---------------------------------------------------------
    # 4. PROCESS EVERY FRAME
    # ---------------------------------------------------------

    for frame_number, result in enumerate(results):

        # YOLO creates an annotated version of this frame
        annotated_frame = result.plot()

        # Write the annotated frame into the output video
        writer.write(annotated_frame)

        # Collect tracking observations
        if result.boxes.id is None:
            continue

        ids = result.boxes.id.tolist()
        boxes = result.boxes.xyxy.tolist()

        for vehicle_id, box in zip(ids, boxes):

            x1, y1, x2, y2 = box

            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            rows.append({
                "frame": frame_number,
                "vehicle_id": int(vehicle_id),
                "center_x": center_x,
                "center_y": center_y
            })

    writer.release()

    subprocess.run([
    FFMPEG_PATH,
    "-i", str(output_path),
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",
    str(h264_output_path)
    ], check=True)

    # ---------------------------------------------------------
    # 5. NO VEHICLES DETECTED
    # ---------------------------------------------------------

    if not rows:
        return {
            "vehicles_detected": 0,
            "busiest_region": None,
            "congestion_score": 0,
            "bottleneck_persistence": 0,
            "regions": [],
            "recommendation": (
                "No vehicles were detected in the uploaded video."
            ),
            "annotated_video": str(output_path)
        }

    df = pd.DataFrame(rows)

    # ---------------------------------------------------------
    # 6. UNIQUE VEHICLE COUNT
    # ---------------------------------------------------------

    unique_vehicles = int(
        df["vehicle_id"].nunique()
    )

    # ---------------------------------------------------------
    # 7. AUTOMATIC REGION CREATION
    # ---------------------------------------------------------

    x_min = df["center_x"].min()
    x_max = df["center_x"].max()

    y_min = df["center_y"].min()
    y_max = df["center_y"].max()

    x_mid = (x_min + x_max) / 2
    y_mid = (y_min + y_max) / 2

    def find_region(x, y):

        if x < x_mid and y < y_mid:
            return "Top-Left"

        elif x >= x_mid and y < y_mid:
            return "Top-Right"

        elif x < x_mid and y >= y_mid:
            return "Bottom-Left"

        else:
            return "Bottom-Right"

    df["region"] = df.apply(
        lambda row: find_region(
            row["center_x"],
            row["center_y"]
        ),
        axis=1
    )

    # ---------------------------------------------------------
    # 8. MOVEMENT BETWEEN FRAMES
    # ---------------------------------------------------------

    df = df.sort_values(
        ["vehicle_id", "frame"]
    )

    df["dx"] = (
        df.groupby("vehicle_id")["center_x"].diff()
    )

    df["dy"] = (
        df.groupby("vehicle_id")["center_y"].diff()
    )

    df["movement"] = np.sqrt(
        df["dx"] ** 2 +
        df["dy"] ** 2
    )

    movement_df = df.dropna(
        subset=["movement"]
    )

    # ---------------------------------------------------------
    # 9. OCCUPANCY BY REGION
    # ---------------------------------------------------------

    occupancy = (
        df.groupby(
            ["frame", "region"]
        )["vehicle_id"]
        .nunique()
        .reset_index(name="vehicles")
    )

    region_occupancy = (
        occupancy.groupby("region")["vehicles"]
        .mean()
        .reset_index(
            name="average_occupancy"
        )
    )

    # ---------------------------------------------------------
    # 10. MOVEMENT BY REGION
    # ---------------------------------------------------------

    region_movement = (
        movement_df.groupby("region")["movement"]
        .mean()
        .reset_index(
            name="average_movement"
        )
    )

    # ---------------------------------------------------------
    # 11. COMBINE TRAFFIC MEASUREMENTS
    # ---------------------------------------------------------

    analysis = region_occupancy.merge(
        region_movement,
        on="region",
        how="left"
    )

    analysis["average_movement"] = (
        analysis["average_movement"]
        .fillna(0)
    )

    # ---------------------------------------------------------
    # 12. CONGESTION SCORE
    # ---------------------------------------------------------

    max_occupancy = (
        analysis["average_occupancy"].max()
    )

    max_movement = (
        analysis["average_movement"].max()
    )

    if max_occupancy > 0:

        analysis["occupancy_normalized"] = (
            analysis["average_occupancy"] /
            max_occupancy
        )

    else:

        analysis["occupancy_normalized"] = 0

    if max_movement > 0:

        analysis["movement_normalized"] = (
            analysis["average_movement"] /
            max_movement
        )

    else:

        analysis["movement_normalized"] = 0

    analysis["congestion_score"] = (
        analysis["occupancy_normalized"] *
        (1 - analysis["movement_normalized"])
    )

    analysis = analysis.sort_values(
        "congestion_score",
        ascending=False
    )

    # ---------------------------------------------------------
    # 13. IDENTIFY HOTSPOT
    # ---------------------------------------------------------

    hotspot = analysis.iloc[0]

    busiest_region = str(
        hotspot["region"]
    )

    congestion_score = float(
        hotspot["congestion_score"]
    )

    # ---------------------------------------------------------
    # 14. BOTTLENECK PERSISTENCE
    # ---------------------------------------------------------

    busiest_per_frame = (
        occupancy.loc[
            occupancy.groupby(
                "frame"
            )["vehicles"].idxmax()
        ]
    )

    total_observed_frames = len(
        busiest_per_frame
    )

    hotspot_frames = int(
        (
            busiest_per_frame["region"]
            == busiest_region
        ).sum()
    )

    if total_observed_frames > 0:

        persistence = (
            hotspot_frames /
            total_observed_frames
        ) * 100

    else:

        persistence = 0

    # ---------------------------------------------------------
    # 15. TRAFFIC RECOMMENDATION
    # ---------------------------------------------------------

    if congestion_score >= 0.6:

        recommendation = (
            f"Potential congestion hotspot detected in "
            f"{busiest_region}. High vehicle occupancy combined "
            f"with relatively low movement was observed. "
            f"Consider investigating traffic signal timing, "
            f"lane management, or queue formation in this zone."
        )

    elif congestion_score >= 0.3:

        recommendation = (
            f"Moderate traffic pressure was observed in "
            f"{busiest_region}. Monitor this zone for persistent "
            f"vehicle accumulation before making traffic-management changes."
        )

    else:

        recommendation = (
            "No strong congestion hotspot was identified from "
            "the available traffic observations."
        )

    # ---------------------------------------------------------
    # 16. PREPARE REGION RESULTS
    # ---------------------------------------------------------

    regions = []

    for _, row in analysis.iterrows():

        regions.append({
            "region": str(
                row["region"]
            ),

            "average_occupancy": round(
                float(
                    row["average_occupancy"]
                ),
                2
            ),

            "average_movement": round(
                float(
                    row["average_movement"]
                ),
                2
            ),

            "congestion_score": round(
                float(
                    row["congestion_score"]
                ),
                3
            )
        })

    # ---------------------------------------------------------
    # 17. FINAL RESULT
    # ---------------------------------------------------------

    return {
        "vehicles_detected": unique_vehicles,

        "busiest_region": busiest_region,

        "congestion_score": round(
            congestion_score,
            3
        ),

        "bottleneck_persistence": round(
            float(persistence),
            2
        ),

        "regions": regions,

        "recommendation": recommendation,

        "annotated_video": str(
            h264_output_path
        )
    }


if __name__ == "__main__":

    video = Path(
        "traffic_video_source2/trafficvideo.mp4"
    )

    result = analyze_video(video)

    print(result)