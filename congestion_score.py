import pandas as pd

occupancy = pd.read_csv("region_occupancy_over_time.csv")
movement = pd.read_csv("region_movement_summary.csv")

# Calculate average occupancy for each region
region_occupancy = (
    occupancy.groupby("region")["vehicles"]
    .mean()
    .reset_index(name="average_occupancy")
)

# Combine occupancy and movement data
df = region_occupancy.merge(
    movement,
    on="region"
)

# Normalize both measurements
df["occupancy_normalized"] = (
    df["average_occupancy"] /
    df["average_occupancy"].max()
)

df["movement_normalized"] = (
    df["average_movement"] /
    df["average_movement"].max()
)

# High occupancy + low movement = higher congestion score
df["congestion_score"] = (
    df["occupancy_normalized"] *
    (1 - df["movement_normalized"])
)

# Show most congested regions first
df = df.sort_values(
    "congestion_score",
    ascending=False
)

print(df)

df.to_csv(
    "congestion_scores.csv",
    index=False
)

print("\nCongestion scores saved.")