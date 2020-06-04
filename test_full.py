import requests
from database_connector import deleteUser,getUserId
import os

root_url = "http://127.0.0.1:5000/"

def test_life():
    response = requests.get(root_url)
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

def test_register_pos():
    username = "testuser"
    password = "blubb"
    data = {
        "username":username,
        "password":password
        }
    response = requests.post(root_url+"register",json=data)
    assert(response.status_code == 200)

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

def test_layerdata():
    query = "features/0/id"
    data = {
        "userid":getUserId("testuser"),
        "layer":"test_layer"
        }
    response = requests.get(root_url+"getLayer/"+query,json=data)
    assert(response.status_code == 200)
    print(response.text)

def test_layerchange_nonexistant():
    query = "nonexistant_layer/features/0/id"
    data = {
        "userid":getUserId("testuser"),
        "data" : -1
        }
    response = requests.post(root_url+"addLayerData/"+query,json=data)
    assert(response.status_code == 400)

def test_layerchange_add():
    import random
    query = "test_layer2/data/1/state"
    data = {
        "userid":getUserId("testuser"),
        "data" : {"somedata":random.randint(0,1000)}
        }
    response = requests.post(root_url+"addLayerData/"+query,json=data)
    assert(response.status_code == 200)

def test_layerchange_add2():
    query = "test_layer2/"
    data = {
        "userid":getUserId("testuser"),
        "data" : {"data": [{"state": 0}, {"state": 2}, {"state": 4}]}
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
        test_layerdata()
        print("test_layerchange_nonexistant")
        test_layerchange_nonexistant()
        print("test_layerchange_add2")
        test_layerchange_add2()
        print("test_layerchange_add")
        test_layerchange_add()
        print("test_layerchange_all")
        test_layerchange_all()
    except AssertionError as e:
        print("^^^^ Failed here ^^^^\n")
        raise e
    else:
        print("\nALL TESTS SUCCESSFULL!\n")
    finally:
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