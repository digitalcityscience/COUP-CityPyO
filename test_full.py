import requests
from database_connector import deleteUser,getUserId
import os

root_url = "http://127.0.0.1:5000/"

def test_life():
    response = requests.get(root_url)
    assert(response.status_code == 200)

def test_register_pos():
    username = "testuser"
    password = "blubb"
    data = {
        "username":username,
        "password":password
        }
    response = requests.post(root_url+"register",json=data)
    assert(response.status_code == 200)

def test_login_pos():
    username = "testuser"
    password = "blubb"
    data = {
        "username":username,
        "password":password
        }
    response = requests.post(root_url+"login",json=data)
    assert(response.status_code == 200)

def test_login_neg_pw():
    username = "testuser"
    password = "falsches_passwort"
    data = {
        "username":username,
        "password":password
        }
    response = requests.post(root_url+"login",json=data)
    assert(response.status_code == 401)

def test_login_neg_user():
    username = "kein_user"
    password = "passwort"
    data = {
        "username":username,
        "password":password
        }
    response = requests.post(root_url+"login",json=data)
    assert(response.status_code == 401)

def test_register_neg():
    username = "testuser"
    password = "neues_passwort"
    data = {
        "username":username,
        "password":password
        }
    response = requests.post(root_url+"register",json=data)
    assert(response.status_code == 403)

def test_layerchange_add_new():
    query = "test_layer"
    data = {
        "userid":getUserId("testuser"),
        "data" : {"type": "FeatureCollection","features": [{ "type": "Feature", "id":0 }]}
        }
    response = requests.post(root_url+"addLayerData/"+query,json=data)
    assert(response.status_code == 200)

def test_layer():
    data = {
        "userid":getUserId("testuser"),
        "layer":"test_layer"
        }
    response = requests.get(root_url+"getLayer",json=data)
    assert(response.status_code == 200)
    print(response.json()["type"])

def test_get_layerdata():
    query = "features/0/id"
    data = {
        "userid":getUserId("testuser"),
        "layer":"test_layer"
        }

    response = requests.post(root_url+"getLayer/"+query,json=data)

    assert(response.status_code == 200)
    print(response.text)


def test_abm_request():
    query = "abmScenario"
    data_without_time_filter = {
        "userid": getUserId("testuser"),
        "scenario_properties": {
            "bridge_1": True,
            "amenities_roof": "random",
            "blocks": "open",
            "bridge_2": False,
            "main_street_orientation": "vertical"
        },
        "agent_filters": {
            "mode": "foot",
            "student_or_adult": "adult",
            "resident_or_visitor": "resident"
        }
    }

    data_with_time_filter = data_without_time_filter.copy()
    data_with_time_filter["time_filters"] = {
            "start_time": 10000.0,
            "end_time": 14000.0
        }

    response_with_time_filter = requests.post(root_url+"getLayer/"+query, json=data_with_time_filter)
    response_without_time_filter = requests.post(root_url+"getLayer/"+query, json=data_without_time_filter)


    assert(response_with_time_filter.status_code == 200)
    assert(response_without_time_filter.status_code == 200)
    print(len(response_without_time_filter.json()["data"]) , len(response_with_time_filter.json()["data"]))
    assert(len(response_without_time_filter.json()["data"]) > len(response_with_time_filter.json()["data"]))


def test_layerchange_nonexistant():
    query = "nonexistant_layer/features/0/id"
    data = {
        "userid":getUserId("testuser"),
        "data" : -1
        }
    response = requests.post(root_url+"addLayerData/"+query,json=data)
    assert(response.status_code == 400)

def test_layerchange_add2():
    query = "test_layer2/"
    data = {
        "userid":getUserId("testuser"),
        "data" : {"data": [{"state": 0}, {"state": 2}, {"state": 4}]}
        }
    response = requests.post(root_url+"addLayerData/"+query,json=data)
    assert(response.status_code == 200)

def test_layerchange_add():
    import random
    query = "test_layer2/data/1/state"
    data = {
        "userid":getUserId("testuser"),
        "data" : {"somedata":random.randint(0,1000)}
        }
    response = requests.post(root_url+"addLayerData/"+query,json=data)
    assert(response.status_code == 200)

def test_layerchange_all():
    query = "test_layer/"
    data = {
        "userid":getUserId("testuser"),
        "data" : {"data": [{"state": 0}, {"state": 2}, {"state": 4}]}
        }
    response = requests.post(root_url+"addLayerData/"+query,json=data)
    assert(response.status_code == 200)

def test_nouser():
    query = "test_layer"
    data = {
        "userid":"189637",
        "data" : -1
        }
    response = requests.post(root_url+"addLayerData/"+query,json=data)
    assert(response.status_code == 401)


def cleanup():
    print("deleting test layers")
    filepath="data/user/"+getUserId("testuser")+"/test_layer.json"
    if os.path.exists(filepath):
        os.remove(filepath)
    filepath="data/user/"+getUserId("testuser")+"/test_layer2.json"
    if os.path.exists(filepath):
        os.remove(filepath)
    filepath="data/user/"+getUserId("testuser")+"/hashes.json"
    if os.path.exists(filepath):
        os.remove(filepath)
    filepath="data/user/"+getUserId("testuser")
    if os.path.exists(filepath):
        os.rmdir(filepath)
    print("deleting test user","testuser")
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
        print("test_layerchange_add_new")
        test_layerchange_add_new()
        print("test_layer")
        test_layer()
        print("test_layerdata")
        test_get_layerdata()
        print("test abm request")
        test_abm_request()
        print("test_layerchange_nonexistant")
        test_layerchange_nonexistant()
        print("test_layerchange_add2")
        test_layerchange_add2()
        print("test_layerchange_add")
        test_layerchange_add()
        print("test_layerchange_all")
        test_layerchange_all()
        print("test_nouser")
        test_nouser()
    except AssertionError as e:
        print("^^^^ Failed here ^^^^\n")
        raise e
    else:
        print("\nALL TESTS SUCCESSFULL!\n")
    finally:
        cleanup()