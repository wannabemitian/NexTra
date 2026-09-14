import json


def get_camera_road(camera_id):
    with open("road_network.json", "r") as file:
        network = json.load(file)

    for camera in network["cameras"]:
        if camera["id"] == camera_id:
            return camera["road"]

    return None


print(get_camera_road("Camera_B"))