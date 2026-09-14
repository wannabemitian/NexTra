import pandas as pd

df = pd.read_csv("vehicle_tracking_data.csv")

df = df.sort_values(["vehicle_id", "frame"])

# Calculate movement between consecutive frames
df["dx"] = df.groupby("vehicle_id")["center_x"].diff()
df["dy"] = df.groupby("vehicle_id")["center_y"].diff()

df["distance"] = (
    (df["dx"] ** 2 + df["dy"] ** 2) ** 0.5
)

# Summarize each vehicle's observed trajectory
trajectory_summary = (
    df.groupby("vehicle_id")
      .agg(
          first_frame=("frame", "min"),
          last_frame=("frame", "max"),
          start_x=("center_x", "first"),
          start_y=("center_y", "first"),
          end_x=("center_x", "last"),
          end_y=("center_y", "last"),
          total_distance=("distance", "sum")
      )
      .reset_index()
)

print("Vehicle trajectory summary:")
print(trajectory_summary)

trajectory_summary.to_csv(
    "vehicle_trajectory_summary.csv",
    index=False
)

print("\nTrajectory data saved.")