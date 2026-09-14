import pandas as pd

data = {
    "vehicle_id": ["V01", "V02", "V03", "V01", "V02", "V04"],
    "camera": ["Camera_A", "Camera_A", "Camera_A", "Camera_B", "Camera_B", "Camera_B"],
    "timestamp": [
        "08:00",
        "08:01",
        "08:03",
        "08:05",
        "08:06",
        "08:07"
    ]
}

df = pd.DataFrame(data)

print(df)