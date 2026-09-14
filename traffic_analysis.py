import pandas as pd

df = pd.read_csv("vehicle_tracking_data.csv")

unique_vehicles = df["vehicle_id"].nunique()

print("Unique vehicles observed:", unique_vehicles)