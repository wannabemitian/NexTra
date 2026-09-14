import pandas as pd

df = pd.read_csv("congestion_over_time.csv")

# A ratio above 1 means occupancy is above that region's average.
df["above_average"] = df["occupancy_ratio"] > 1

# Calculate how often each region is above its normal occupancy.
persistence = (
    df.groupby("region")["above_average"]
    .mean()
    .reset_index(name="persistence")
)

# Convert to percentage
persistence["persistence_percent"] = (
    persistence["persistence"] * 100
)

# Highest persistence first
persistence = persistence.sort_values(
    "persistence_percent",
    ascending=False
)

print(persistence)

persistence.to_csv(
    "congestion_persistence_results.csv",
    index=False
)

print("\nPersistence results saved.")