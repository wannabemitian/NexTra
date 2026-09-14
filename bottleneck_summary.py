import pandas as pd

df = pd.read_csv("busiest_region_over_time.csv")

# Count how many frames each region was the busiest
summary = (
    df["region"]
    .value_counts()
    .reset_index()
)

summary.columns = ["region", "frames_as_busiest"]

# Calculate the percentage of the video
total_frames = len(df)

summary["percentage_of_video"] = (
    summary["frames_as_busiest"] / total_frames * 100
)

print(summary)

summary.to_csv(
    "bottleneck_summary.csv",
    index=False
)

print("\nBottleneck summary saved.")