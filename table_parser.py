import json
import os
from shapely.geometry import Polygon, Point, mapping
from shapely import affinity
import pyproj
import json

# websocket
import asyncio
import websockets

# http
import requests
from requests.auth import HTTPBasicAuth


marker_side_length = 3.2
cwd = os.getcwd()

# entire competition area
#extend_north = 5932375.29501040372997522
#extend_south = 5931094.97593854926526546
#extend_west = 566523.05231103568803519
#extend_east = 567293.41378647310193628

# northern grasbrook penisula
extend_north = 5932575.29501040372997522
extend_south = 5931661
extend_west = 566835
extend_east = 567749

#table_res = 2000  # px per direction # entire table
table_res = 1000  # px per direction # 1 box


table_reference_point = Point(extend_west, extend_south)

table_scale_y = (extend_north - extend_south) / table_res
table_scale_x = (extend_east - extend_west) / table_res



def find_corner_point(feature):
    with open(cwd + "/" + "building_corners" + ".geojson", "r") as f:
        corners_json = json.load(f)

    building_id = feature["properties"]["id"]

    for corner in corners_json["features"]:
        if corner["properties"]["id"] == building_id:
            return corner["geometry"]["coordinates"]


def get_marker_centroid(first_corner_x, first_corner_y):
    marker_polygon_coords = [
        [first_corner_x, first_corner_y],
        [first_corner_x + marker_side_length, first_corner_y],
        [first_corner_x + marker_side_length, first_corner_y + marker_side_length],
        [first_corner_x, first_corner_y + marker_side_length],
        [first_corner_x, first_corner_y]
    ]

    marker_poly = Polygon(marker_polygon_coords)

    marker_centroid = marker_poly.centroid

    return [marker_centroid.x - first_corner_x, marker_centroid.y- first_corner_y]


def produce_test_buildings():
    cwd = os.getcwd()

    with open(cwd + "/" + "test_buildings" + ".geojson", "r") as g:
        buildings_json = json.load(g)

    normalized_features = []
    buildings_copy = buildings_json["features"].copy()

    for feature in buildings_copy:
        first_corner_x, first_corner_y = find_corner_point(feature)
        for coordinate in feature["geometry"]["coordinates"][0][0]:
            coordinate[0] = coordinate[0] - first_corner_x
            coordinate[1] = coordinate[1] - first_corner_y

        feature["properties"]["marker_centroid"] = get_marker_centroid(first_corner_x, first_corner_y)

        normalized_features.append(feature)

    buildings_json["features"] = normalized_features

    with open(cwd + "/" + "buildings.json", "w") as fp:
        json.dump(buildings_json, fp)


def find_matching_building_for_marker(building_library, marker_key):
    for building in building_library["features"]:
        if building["properties"]["id"] == marker_key:
            return building

    return None


def get_building_geometry(building, current_marker_centroid, rotatation):
    translated_coords = []

    for coordinate in building["geometry"]["coordinates"][0]:
        coordinate_x = table_scale_x * (coordinate[0] + current_marker_centroid[0] - marker_side_length) + table_reference_point.x
        coordinate_y = table_scale_y * (coordinate[1] + current_marker_centroid[1] - marker_side_length) + table_reference_point.y

        translated_coords.append([coordinate_x, coordinate_y])

    building_first_corner = Point([
        table_reference_point.x + (current_marker_centroid[0] - marker_side_length) * table_scale_x,
        table_reference_point.y + (current_marker_centroid[1] - marker_side_length) * table_scale_y
    ])
    building_poly = Polygon(translated_coords)
    building_poly = affinity.rotate(building_poly, rotatation, origin=building_first_corner, use_radians=True)

    return mapping(building_poly)


# receives a geojson, reprojects it and returns the reprojected geojson
def reproject_geojson_utm_to_geodesic(local_geojson):
    global_epsg = 'EPSG:4326'
    local_epsg = 'EPSG:25832'

    local_prj = pyproj.Proj("+init=" + local_epsg)
    global_prj = pyproj.Proj("+init=" + global_epsg)

    features = local_geojson['features']

    # creates a list of coordinates used in the feature
    for feature_id, feature in enumerate(features):
        local_coords = []

        feature_length = len(feature['geometry']['coordinates'][0])
        coordinates = feature['geometry']['coordinates'][0]
        for point in coordinates:
            local_coords.append((point[0], point[1]))

        # reprojects local coords and updates features with reprojected coords
        point_counter = 0
        for gc in pyproj.itransform(local_prj, global_prj, local_coords):
            features[feature_id]['geometry']['coordinates'][0][point_counter % feature_length] = gc

            point_counter += 1

    projected_features = features
    local_geojson['features'] = projected_features

    return local_geojson



def parse_table_state(table_state):


    buildings_utm_features = []

    print(table_scale_x, table_scale_y)

    # iterate over all markers in the table output
    for key, value in table_state.items():
        # 1 [[0, 65], -1.1839206090638685]
        key = int(key)
        print("building id", key)
        current_marker_centroid = value[0]
        rotation_rad = value[1]
        print(current_marker_centroid, rotation_rad)

        building = find_matching_building_for_marker(building_library, key)

        if building == None:
            continue

        geom = get_building_geometry(building, current_marker_centroid, rotation_rad)

        feature = {
            "type": "Feature",
            "id": building["properties"]["id"],
            "geometry": geom,
            "properties": {
                "land_use_detailed_type": "commercialOffice",
                "height": 16,
                "color": "#ff00ff",
                "element_id": 2528131.0,
                "plot_id": 17.0,
                "building_id": "Q1-17-02",
                "area_planning_type": "unknown land use type",
                "floor_area": 737.9999150096554
            }
        }

        buildings_utm_features.append(feature)

    buildings_utm_geojson = {
        "type": "FeatureCollection",
        "name": "horizontal_complementary",
        "features": buildings_utm_features
    }

    buildings_wgs_geojson = reproject_geojson_utm_to_geodesic(json.loads(json.dumps(buildings_utm_geojson)))
    #buildings_wgs_geojson = buildings_utm_geojson

    with open(cwd + "/" + "lego_set_2.json", "w") as fp:
        json.dump(buildings_wgs_geojson, fp)

    return buildings_wgs_geojson



def send_http_request(payload):
    # post_address = 'https://nc.hcu-hamburg.de/cityPyo/updateTableData'
    post_address = 'http://0.0.0.0:5000/updateTableData'

    r = requests.post(post_address, auth=HTTPBasicAuth('grasbrooker', '%3gZabBC4g3Eu'), json=payload, headers={'Content-Type': 'application/json'})
    print(r)

    if not r.status_code == 200:
        print("could not post result to cityPYO", post_address)
        print("Error code", r.status_code)
    else:
        print("Successfully posted to cityPYO", post_address, r.status_code)


def callWebSocket(uri, messageType, message):
        asyncio.get_event_loop().run_until_complete(
            sendSocketMessage(uri, messageType, message))

async def sendSocketMessage(uri, messageType, message):
        async with websockets.connect(uri) as websocket:
            data = {messageType: message}
            await websocket.send(json.dumps(data))

def callWebSocketJson(uri, data):
        asyncio.get_event_loop().run_until_complete(
            sendSocketMessage(uri, data))

async def sendJsonSocketMessage(uri, data):
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps(data))


if __name__ == '__main__':
    import time

    with open(cwd + "/" + "buildings_library" + ".json", "r") as fg:
        building_library = json.load(fg)


   # produce_test_buildings()
    with open(cwd + "/" + "table_output" + ".json", "r") as f:
        table_json = json.load(f)


    for i in range(1,1000):
        for building_id in range(1,4):
            table_json[str(building_id)][0][0] += 10
            table_json[str(building_id)][0][1] += 10
            table_json[str(building_id)][1] += 0.5

        geojson = parse_table_state(table_json)
        start_time = time.time()


        callWebSocket("ws://fierce-dawn-73363.herokuapp.com", 'detectedGeoJson', json.dumps(geojson))
        end_time = time.time()

        print("time")
        print((end_time-start_time))


    # while True:
    #     for i in range(1,3):
    #         with open(cwd + "/" + "lego_set_" + str(i) + ".json", "r") as f:
    #             geojson = json.load(f)
    #
    #         callWebSocket("ws://fierce-dawn-73363.herokuapp.com", 'detectedGeoJson', json.dumps(geojson))









