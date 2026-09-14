import cv2
import pandas as pd

video_path = "traffic_video_source2/trafficvideo.mp4"

tracking = pd.read_csv("vehicle_tracking_data_with_regions.csv")
scores = pd.read_csv("congestion_scores.csv")

# Region with the highest congestion score
bottleneck_region = scores.iloc[0]["region"]

cap = cv2.VideoCapture(video_path)

while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1

    current = tracking[
        tracking["frame"] == frame_number
    ]

    # Draw tracked vehicle positions
    for _, vehicle in current.iterrows():

        x = int(vehicle["center_x"])
        y = int(vehicle["center_y"])

        cv2.circle(
            frame,
            (x, y),
            5,
            (0, 255, 0),
            -1
        )

    # Display detected bottleneck
    cv2.putText(
        frame,
        f"Candidate bottleneck: {bottleneck_region}",
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        2
    )

    cv2.imshow("Traffic Analysis", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()