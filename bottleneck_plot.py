import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("busiest_region_over_time.csv")

# Count how many frames each region was the busiest
summary = df["region"].value_counts()

summary.plot(
    kind="bar",
    figsize=(10, 6)
)

plt.title("Busiest Region Across the Video")
plt.xlabel("Region")
plt.ylabel("Number of Frames")
plt.xticks(rotation=0)
plt.grid(axis="y")
plt.show()