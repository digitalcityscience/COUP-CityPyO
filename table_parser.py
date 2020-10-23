import json
import os
from shapely.geometry import Polygon, Point, mapping
from shapely import affinity
import pyproj

marker_side_length = 3.2
table_reference_point = Point(566983.28, 5932038.94)
cwd = os.getcwd()


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

    for coordinate in building["geometry"]["coordinates"][0][0]:
        coordinate_x = (coordinate[0] + current_marker_centroid[0] - marker_side_length) + table_reference_point.x
        coordinate_y = coordinate[1] + current_marker_centroid[1] - marker_side_length + table_reference_point.y

        translated_coords.append([coordinate_x, coordinate_y])

    building_first_corner = Point([
        table_reference_point.x + current_marker_centroid[0] - marker_side_length,
        table_reference_point.y + current_marker_centroid[1] - marker_side_length
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

    with open(cwd + "/" + "buildings_library" + ".json", "r") as fg:
        building_library = json.load(fg)

    buildings_utm_features = []

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
                "height": 5.5,
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


    with open(cwd + "/" + "buildings_out_utm.json", "w") as fp:
        json.dump(buildings_utm_geojson, fp)


    with open(cwd + "/" + "buildings_out_utm" + ".json", "r") as t:
        # json.parse(json.serialize) as a fix since all coordinates are immutable tuples in geom
        buildings_utm_json = json.load(t)
        buildings_wgs_geojson = reproject_geojson_utm_to_geodesic(buildings_utm_json)


    return buildings_wgs_geojson

    with open(cwd + "/" + "buildings_out_wgs.json", "w") as fp:
        json.dump(buildings_wgs_geojson, fp)



if __name__ == '__main__':
    #produce_test_buildings()
    with open(cwd + "/" + "table_output" + ".json", "r") as f:
        table_json = json.load(f)

    parse_table_state(table_json)





