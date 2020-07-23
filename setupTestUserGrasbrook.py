import requests
from database_connector import getUserId

root_url = "http://127.0.0.1:5000/"


data_sources = {
    "groundfloor": "https://raw.githubusercontent.com/grasbrook-cityscope/pyParseXls2GeoJson/master/results/groundfloor.geojson",
    "upperfloor":  "https://raw.githubusercontent.com/grasbrook-cityscope/pyParseXls2GeoJson/master/results/upperfloor.geojson",
    "spaces":   "https://raw.githubusercontent.com/grasbrook-cityscope/pyParseXls2GeoJson/master/results/spaces.geojson",
}

def register_ernie():
    username = "ernie"
    password = "bert"
    data = {
        "username":username,
        "password":password
        }
    response = requests.post(root_url+"register",json=data)
    assert(response.status_code == 200)


def create_base_layers():

    for name, address in data_sources.items():
        query = name
        data = {
            "userid": getUserId("ernie"),
            "data": requests.get(address).json()
        }

        response = requests.post(root_url + "addLayerData/" + query, json=data)
        assert (response.status_code == 200)


if __name__ == "__main__":
    register_ernie()
    create_base_layers()