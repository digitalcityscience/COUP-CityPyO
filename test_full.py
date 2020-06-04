import requests

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
    username = "neuer_user"
    password = "neues_passwort"
    data = {
        "username":username,
        "password":password
        }
    response = requests.post(root_url+"register",json=data)
    assert(response.status_code == 200)

    from database_connector import deleteUser
    print("deleting test entry",response.json())
    deleteUser(response.json()["user_id"])

def test_register_neg():
    username = "testuser"
    password = "neues_passwort"
    data = {
        "username":username,
        "password":password
        }
    response = requests.post(root_url+"register",json=data)
    assert(response.status_code == 403)

def test_layer():
    data = {
        "userid":"e3b205abbda908571fa09d99bac58ef9",
        "layer":"features_buildings"
        }
    response = requests.get(root_url+"getLayer",json=data)
    assert(response.status_code == 200)
    print(response.json()["type"])

def test_layerdata():
    query = "features/0/id"
    data = {
        "userid":"e3b205abbda908571fa09d99bac58ef9",
        "layer":"features_buildings"
        }
    response = requests.get(root_url+"getLayer/"+query,json=data)
    assert(response.status_code == 200)
    print(response.text)

def test_layerchange_nonexistant():
    query = "nonexistant_layer/features/0/id"
    data = {
        "userid":"e3b205abbda908571fa09d99bac58ef9",
        "data" : -1
        }
    response = requests.post(root_url+"addLayerData/"+query,json=data)
    assert(response.status_code == 400)

def test_layerchange_add():
    import random
    query = "test_layer/data/1/state"
    data = {
        "userid":"e3b205abbda908571fa09d99bac58ef9",
        "data" : {"somedata":random.randint(0,1000)}
        }
    response = requests.post(root_url+"addLayerData/"+query,json=data)
    assert(response.status_code == 200)

def test_layerchange_add2():
    query = "test_layer2/"
    data = {
        "userid":"e3b205abbda908571fa09d99bac58ef9",
        "data" : {"somedata":1337}
        }
    response = requests.post(root_url+"addLayerData/"+query,json=data)
    assert(response.status_code == 200)
    import os
    os.remove("data/user/e3b205abbda908571fa09d99bac58ef9/test_layer2.json")

def test_layerchange_all():
    query = "test_layer/"
    data = {
        "userid":"e3b205abbda908571fa09d99bac58ef9",
        "data" : {"data": [{"state": 0}, {"state": 2}, {"state": 4}]}
        }
    response = requests.post(root_url+"addLayerData/"+query,json=data)
    assert(response.status_code == 200)

if __name__ == "__main__":
    print("test_life")
    test_life()
    print("test_login_pos")
    test_login_pos()
    print("test_login_neg_pw")
    test_login_neg_pw()
    print("test_login_neg_user")
    test_login_neg_user()
    print("test_register_pos")
    test_register_pos()
    print("test_register_neg")
    test_register_neg()

    print("test_layer")
    test_layer()
    print("test_layerdata")
    test_layerdata()
    print("test_layerchange_nonexistant")
    test_layerchange_nonexistant()
    print("test_layerchange_add")
    test_layerchange_add()
    print("test_layerchange_add2")
    test_layerchange_add2()
    print("test_layerchange_all")
    test_layerchange_all()