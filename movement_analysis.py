import pandas as pd
import numpy as np

df = pd.read_csv("vehicle_tracking_data.csv")

# Sort observations so each vehicle's frames are in chronological order
df = df.sort_values(["vehicle_id", "frame"])

# Find the change in position from one frame to the next
df["dx"] = df.groupby("vehicle_id")["center_x"].diff()
df["dy"] = df.groupby("vehicle_id")["center_y"].diff()

# Calculate distance travelled between consecutive frames
df["movement"] = np.sqrt(
    df["dx"] ** 2 + df["dy"] ** 2
)

print(df.head(20))

df.to_csv("vehicle_movement_data.csv", index=False)

print("\nMovement data saved.")