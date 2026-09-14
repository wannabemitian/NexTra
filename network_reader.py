import json

with open("road_network.json", "r") as file:
    network = json.load(file)

for camera in network["cameras"]:
    print(
        camera["id"],
        "is monitoring",
        camera["road"]
    )