import pandas as pd

occupancy = pd.read_csv("region_occupancy_over_time.csv")

# Calculate average occupancy across the video
average_occupancy = (
    occupancy.groupby("region")["vehicles"]
    .mean()
    .reset_index(name="average_occupancy")
)

# Add the average occupancy back to every frame
df = occupancy.merge(
    average_occupancy,
    on="region"
)

# Compare each frame with that region's normal occupancy
df["occupancy_ratio"] = (
    df["vehicles"] / df["average_occupancy"]
)

# Sort by frame so we can observe how traffic changes
df = df.sort_values(["region", "frame"])

print(df.head(20))

df.to_csv(
    "congestion_over_time.csv",
    index=False
)

print("\nTime-based congestion data saved.")