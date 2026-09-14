import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("region_occupancy_over_time.csv")

# Put each region into its own column
occupancy = df.pivot(
    index="frame",
    columns="region",
    values="vehicles"
).fillna(0)

# Plot occupancy over time
occupancy.plot(figsize=(12, 6))

plt.title("Traffic Occupancy Over Time")
plt.xlabel("Frame")
plt.ylabel("Number of Vehicles")
plt.legend(title="Region")
plt.grid()
plt.show()