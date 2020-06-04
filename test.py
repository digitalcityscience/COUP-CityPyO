import requests

def life_test():
    response = requests.get("http://127.0.0.1:5000")
    assert(response.status_code == 200)

def login_pos_test():
    username = "testuser"
    password = "blubb"
    data = {
        "username":username,
        "password":password
        }
    response = requests.post("http://127.0.0.1:5000/login",json=data)
    assert(response.status_code == 200)

def login_neg_pw_test():
    username = "testuser"
    password = "falsches_passwort"
    data = {
        "username":username,
        "password":password
        }
    response = requests.post("http://127.0.0.1:5000/login",json=data)
    assert(response.status_code == 401)

def login_neg_user_test():
    username = "kein_user"
    password = "passwort"
    data = {
        "username":username,
        "password":password
        }
    response = requests.post("http://127.0.0.1:5000/login",json=data)
    assert(response.status_code == 401)

def register_pos_test():
    username = "neuer_user"
    password = "neues_passwort"
    data = {
        "username":username,
        "password":password
        }
    response = requests.post("http://127.0.0.1:5000/register",json=data)
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
    response = requests.post("http://127.0.0.1:5000/register",json=data)
    assert(response.status_code == 403)

if __name__ == "__main__":
    life_test()
    login_pos_test()
    login_neg_pw_test()
    login_neg_user_test()
    register_pos_test()
    register_neg_test()
    print("all tests passed!")