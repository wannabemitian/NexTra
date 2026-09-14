import pandas as pd

occupancy = pd.read_csv("region_occupancy_over_time.csv")

# Average occupancy for each region at each frame
region_occupancy = (
    occupancy.groupby(["frame", "region"])["vehicles"]
    .mean()
    .reset_index()
)

# Find the busiest region at every frame
busiest_regions = (
    region_occupancy.loc[
        region_occupancy.groupby("frame")["vehicles"].idxmax()
    ]
)

print(busiest_regions.head(20))

busiest_regions.to_csv(
    "busiest_region_over_time.csv",
    index=False
)

print("\nBusiest-region data saved.")