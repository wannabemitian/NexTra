import pandas as pd

movement = pd.read_csv("vehicle_movement_data.csv")
regions = pd.read_csv("vehicle_tracking_data_with_regions.csv")

df = movement.merge(
    regions[["frame", "vehicle_id", "region"]],
    on=["frame", "vehicle_id"],
    how="left"
)

region_movement = (
    df.groupby("region")["movement"]
      .mean()
      .reset_index(name="average_movement")
)

print(region_movement)

region_movement.to_csv(
    "region_movement_summary.csv",
    index=False
)

print("\nMovement summary saved.")