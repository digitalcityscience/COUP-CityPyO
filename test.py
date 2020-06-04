import requests

root_url = "http://127.0.0.1:5000/"

def life_test():
    response = requests.get(root_url)
    assert(response.status_code == 200)

def login_pos_test():
    username = "testuser"
    password = "blubb"
    data = {
        "username":username,
        "password":password
        }
    response = requests.post(root_url+"login",json=data)
    assert(response.status_code == 200)

def login_neg_pw_test():
    username = "testuser"
    password = "falsches_passwort"
    data = {
        "username":username,
        "password":password
        }
    response = requests.post(root_url+"login",json=data)
    assert(response.status_code == 401)

def login_neg_user_test():
    username = "kein_user"
    password = "passwort"
    data = {
        "username":username,
        "password":password
        }
    response = requests.post(root_url+"login",json=data)
    assert(response.status_code == 401)

def register_pos_test():
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

def register_neg_test():
    username = "testuser"
    password = "neues_passwort"
    data = {
        "username":username,
        "password":password
        }
    response = requests.post(root_url+"register",json=data)
    assert(response.status_code == 403)

def layer_test():
    data = {
        "userid":"e3b205abbda908571fa09d99bac58ef9",
        "layer":"features_buildings"
        }
    response = requests.get(root_url+"getLayer",json=data)
    assert(response.status_code == 200)
    print(response.json()["type"])

def layerdata_test():
    query = "features/0/id"
    data = {
        "userid":"e3b205abbda908571fa09d99bac58ef9",
        "layer":"features_buildings"
        }
    response = requests.get(root_url+"getLayer/"+query,json=data)
    assert(response.status_code == 200)
    print(response.text)

def layerchange_nonexistant_test():
    query = "nonexistant_layer/features/0/id"
    data = {
        "userid":"e3b205abbda908571fa09d99bac58ef9",
        "data" : -1
        }
    response = requests.get(root_url+"addLayerData/"+query,json=data)
    assert(response.status_code == 400)

def layerchange_add_test():
    import random
    query = "test_layer/data/1/state"
    data = {
        "userid":"e3b205abbda908571fa09d99bac58ef9",
        "data" : {"somedata":random.randint(0,1000)}
        }
    response = requests.get(root_url+"addLayerData/"+query,json=data)
    assert(response.status_code == 200)

def layerchange_add_test2():
    query = "test_layer2/"
    data = {
        "userid":"e3b205abbda908571fa09d99bac58ef9",
        "data" : {"somedata":1337}
        }
    response = requests.get(root_url+"addLayerData/"+query,json=data)
    assert(response.status_code == 200)
    import os
    os.remove("data/user/e3b205abbda908571fa09d99bac58ef9/test_layer2.json")

def layerchange_all_test():
    query = "test_layer/"
    data = {
        "userid":"e3b205abbda908571fa09d99bac58ef9",
        "data" : {"data": [{"state": 0}, {"state": 2}, {"state": 4}]}
        }
    response = requests.get(root_url+"addLayerData/"+query,json=data)
    assert(response.status_code == 200)

if __name__ == "__main__":
    print("life_test")
    life_test()
    print("login_pos_test")
    login_pos_test()
    print("login_neg_pw_test")
    login_neg_pw_test()
    print("login_neg_user_test")
    login_neg_user_test()
    print("register_pos_test")
    register_pos_test()
    print("register_neg_test")
    register_neg_test()

    print("layer_test")
    layer_test()
    print("layerdata_test")
    layerdata_test()
    print("layerchange_nonexistant_test")
    layerchange_nonexistant_test()
    print("layerchange_add_test")
    layerchange_add_test()
    print("layerchange_add_test2")
    layerchange_add_test2()
    print("layerchange_all_test")
    layerchange_all_test()