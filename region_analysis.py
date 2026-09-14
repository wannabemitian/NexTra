import pandas as pd

df = pd.read_csv("vehicle_tracking_data.csv")

# Find the coordinate boundaries automatically
x_min = df["center_x"].min()
x_max = df["center_x"].max()

y_min = df["center_y"].min()
y_max = df["center_y"].max()

# Find the midpoint of the coordinate space
x_mid = (x_min + x_max) / 2
y_mid = (y_min + y_max) / 2


def find_region(x, y):
    if x < x_mid and y < y_mid:
        return "Top-Left"

    elif x >= x_mid and y < y_mid:
        return "Top-Right"

    elif x < x_mid and y >= y_mid:
        return "Bottom-Left"

    else:
        return "Bottom-Right"


df["region"] = df.apply(
    lambda row: find_region(row["center_x"], row["center_y"]),
    axis=1
)

print(df.head(20))
df.to_csv("vehicle_tracking_data_with_regions.csv", index=False)

print("Regional data saved.")
print("\nRegion distribution:")
print(df["region"].value_counts())