import requests
from database_connector import deleteUser, getUserId
import os
import json
import shutil


root_url = "http://127.0.0.1:5000/"


def test_life():
    response = requests.get(root_url)
    assert response.status_code == 200


def test_register_pos():
    username = "testuser"
    password = "blubb"
    data = {"username": username, "password": password, "context": "grasbrook"}
    response = requests.post(root_url + "register", json=data)
    assert response.status_code == 200
    print("registered user")


def test_login_pos():
    username = "testuser"
    password = "blubb"
    data = {"username": username, "password": password}
    response = requests.post(root_url + "login", json=data)
    print(response)
    print(response.status_code)
    assert response.status_code == 200


def test_login_neg_pw():
    username = "testuser"
    password = "falsches_passwort"
    data = {"username": username, "password": password}
    response = requests.post(root_url + "login", json=data)
    assert response.status_code == 401


def test_login_neg_user():
    username = "kein_user"
    password = "passwort"
    data = {"username": username, "password": password}
    response = requests.post(root_url + "login", json=data)
    assert response.status_code == 401


def test_register_neg():
    username = "testuser"
    password = "neues_passwort"
    data = {"username": username, "password": password}
    response = requests.post(root_url + "register", json=data)
    assert response.status_code == 403


def test_layerchange_add_new_geojson_layer():
    query = "test_layer"
    data = {
        "userid": getUserId("testuser"),
        "data": {
            "features": [get_geojson_test_feature(to_have_id=0, to_be_valid=True)]
        },
    }
    response = requests.post(root_url + "addLayerData/" + query, json=data)
    assert response.status_code == 200


def test_layerchange_add_new_geojson_layer_invalid():
    query = "test_layer_invalid"
    data = {
        "userid": getUserId("testuser"),
        "data": {
            "features": [get_geojson_test_feature(to_have_id=0, to_be_valid=False)]
        },
    }
    response = requests.post(root_url + "addLayerData/" + query, json=data)
    assert response.status_code == 400


def test_get_entire_layer():
    data = {"userid": getUserId("testuser"), "layer": "test_layer"}
    response = requests.get(root_url + "getLayer", json=data)
    assert response.status_code == 200


def test_get_layerdata_single_prop():
    query = "features/0/id"
    data = {"userid": getUserId("testuser"), "layer": "test_layer"}

    response = requests.post(root_url + "getLayer/" + query, json=data)

    assert response.status_code == 200


def test_layerchange_nonexistant():
    query = "nonexistant_layer/features/0/id"
    data = {"userid": getUserId("testuser"), "data": -1}
    response = requests.post(root_url + "addLayerData/" + query, json=data)
    assert response.status_code == 400


def test_layerchange_add_new_data_layer():
    query = "test_layer2/"
    data = {
        "userid": getUserId("testuser"),
        "data": {"data": [{"state": 0}, {"state": 2}, {"state": 4}]},
    }
    response = requests.post(root_url + "addLayerData/" + query, json=data)
    assert response.status_code == 200


def test_update_data_layer_single_prop():
    import random

    query = "test_layer2/data/1/state"
    data = {
        "userid": getUserId("testuser"),
        "data": {"somedata": random.randint(0, 1000)},
    }
    response = requests.post(root_url + "addLayerData/" + query, json=data)
    assert response.status_code == 200


def test_layerchange_update_geojson_feature():
    query = "test_layer/features/0/"
    data = {
        "userid": getUserId("testuser"),
        "data": get_geojson_test_feature(to_have_id=1, to_be_valid=True),
    }
    response = requests.post(root_url + "addLayerData/" + query, json=data)
    assert response.status_code == 200


def test_layerchange_update_geojson_feature_invalid_but_fixable():
    query = "test_layer/features/0/"
    data = {
        "userid": getUserId("testuser"),
        "data": get_geojson_test_feature(
            to_have_id=1, to_be_valid=False, to_be_fixable=True
        ),
    }
    response = requests.post(root_url + "addLayerData/" + query, json=data)
    assert response.status_code == 200


def test_layerchange_update_geojson_feature_invalid():
    query = "test_layer/features/0/"
    data = {
        "userid": getUserId("testuser"),
        "data": get_geojson_test_feature(to_have_id=1, to_be_valid=False),
    }
    response = requests.post(root_url + "addLayerData/" + query, json=data)
    assert response.status_code == 400


def test_update_data_layer_all():
    query = "test_layer/"
    data = {
        "userid": getUserId("testuser"),
        "data": {"data": [{"state": 0}, {"state": 2}, {"state": 4}]},
    }
    response = requests.post(root_url + "addLayerData/" + query, json=data)
    assert response.status_code == 200


def test_nouser():
    query = "test_layer"
    data = {"userid": "189637", "data": -1}
    response = requests.post(root_url + "addLayerData/" + query, json=data)
    assert response.status_code == 401


def test_abm_request():
    # make user not restricted
    user_db_file = "data/users.json"
    userid = getUserId("testuser")

    with open(user_db_file, "r") as jsonread:
        jsondata = json.load(jsonread)
        jsondata[userid]["restricted"] = False

    with open(user_db_file, "w") as jsonwrite:
        json.dump(jsondata, jsonwrite)

    add_abm_test_data(userid)

    query = "abmScenario"
    data = {
        "userid": userid,
        "scenario_properties": {
            "bridge_1": True,
            "bridge_2": False,
            "blocks": "open",
            "main_street_orientation": "vertical",
            "roof_amenities": "random",
        },
    }

    response = requests.post(root_url + "getLayer/" + query, json=data)

    assert response.status_code == 200


def get_geojson_test_feature(
    to_have_id: int, to_be_valid: bool, to_be_fixable: bool = False
):
    valid_coordinates = [
        [[10.0, 53.5], [10.1, 53.5], [10.1, 53.6], [10.0, 53.6], [10.0, 53.5]]
    ]
    fixable_coordinates = [
        [[10.0, 53.5], [10.1, 53.5], [10.0, 53.5], [10.1, 53.6], [10.0, 53.6]]
    ]  # self intersecting bowtie
    invalid_coordinates = [[[10.0, 53.5]]]  # invalid poly with only 1 coord

    geojson_test_feature_trunk = {
        "type": "Feature",
        "id": None,
        "properties": {"test_prop": "test_value"},
        "geometry": {"type": "Polygon", "coordinates": []},
    }

    test_feature = geojson_test_feature_trunk.copy()
    test_feature["id"] = to_have_id
    if not to_be_valid:
        if to_be_fixable:
            test_feature["geometry"]["coordinates"] = fixable_coordinates
        else:
            test_feature["geometry"]["coordinates"] = invalid_coordinates
    else:
        test_feature["geometry"]["coordinates"] = valid_coordinates

    return test_feature


def add_abm_test_data(userid):
    scenarios = {
        "scenario_1": {
            "bridge_1": True,
            "bridge_2": False,
            "blocks": "open",
            "main_street_orientation": "vertical",
            "roof_amenities": "random",
        },
        "scenario_2": {
            "brige_1": False,
            "bridge_2": True,
            "blocks": "open",
            "main_street_orientation": "vertical",
            "roof_amenities": "random",
        },
    }

    amenities = {"vertical_random": {"features": []}}

    with open("data/" + "user/" + userid + "/abmScenarios.json", "w") as jsonfile:
        json.dump(scenarios, jsonfile)
    with open("data/" + "user/" + userid + "/abmAmenities.json", "w") as jsonfile:
        json.dump(amenities, jsonfile)

    if not os.path.exists("data" + "/" + "user" "/" + userid + "/" + "abm"):
        os.mkdir("data" + "/" + "user" + "/" + userid + "/" + "abm")
    with open(
        "data" + "/" + "user" + "/" + userid + "/" + "abm" + "/" + "scenario_1.json",
        "w+",
    ) as jsonfile:
        jsondata = {
            "data": [
                {
                    "agent": {
                        "source": "1-02_work-leisure-home.csv",
                        "id": "worker_visitor1266",
                        "mode": "foot",
                        "student_or_adult": "adult",
                        "resident_or_visitor": "resident",
                    },
                    "timestamps": [56760.0, 56880.0],
                    "path": [
                        ["10.029116616518474", "53.52583144920887"],
                        ["10.030062856331478", "53.52693663639755"],
                    ],
                }
            ]
        }

        json.dump(jsondata, jsonfile)


def cleanup():
    print("deleting test layers")
    filepath = "data/user/" + getUserId("testuser") + "/test_layer.json"
    if os.path.exists(filepath):
        os.remove(filepath)
    filepath = "data/user/" + getUserId("testuser") + "/test_layer2.json"
    if os.path.exists(filepath):
        os.remove(filepath)
    filepath = "data/user/" + getUserId("testuser") + "/hashes.json"
    if os.path.exists(filepath):
        os.remove(filepath)
    filepath = "data/user/" + getUserId("testuser")
    if os.path.exists(filepath):
        shutil.rmtree(filepath)
    print("deleting test user", "testuser")
    deleteUser(getUserId("testuser"))


if __name__ == "__main__":
    try:
        print("test_life")
        test_life()
        print("test_register_pos")
        test_register_pos()
        print("test_login_pos")
        test_login_pos()
        print("test_login_neg_pw")
        test_login_neg_pw()
        print("test_login_neg_user")
        test_login_neg_user()
        print("test_register_neg")
        test_register_neg()
        print("test_layerchange_add_new_geojson_layer")
        test_layerchange_add_new_geojson_layer()
        print("test_layerchange_add_new_geojson_layer_invalid")
        test_layerchange_add_new_geojson_layer_invalid()
        print("test_layer")
        test_get_entire_layer()
        print("test_get_layerdata_single_prop")
        test_get_layerdata_single_prop()
        print("test_layerchange_nonexistant")
        test_layerchange_nonexistant()
        print("test_layerchange_add_geojson_feature")
        test_layerchange_update_geojson_feature()
        print("test_layerchange_add_geojsonfeature_invalid_but_fixable")
        test_layerchange_update_geojson_feature_invalid_but_fixable()
        print("test_layerchange_add_geojsonfeature_invalid")
        test_layerchange_update_geojson_feature_invalid()
        print("test_layerchange_add_new_data_layer")
        test_layerchange_add_new_data_layer()
        print("test_update_data_layer_single_prop")
        test_update_data_layer_single_prop()
        print("test_update_data_layer_all")
        test_update_data_layer_all()
        print("test_nouser")
        test_nouser()
        print("test abm request")
        test_abm_request()
    except AssertionError as e:
        print("^^^^ Failed here ^^^^\n")
        raise e
    else:
        print("\nALL TESTS SUCCESSFULL!\n")
    finally:
        print("yeah")
        # cleanup()
