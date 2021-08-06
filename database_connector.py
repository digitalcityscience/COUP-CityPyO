import os
import json
import datetime
import random

user_db_file = "data/users.json"

def getUserId(username):

    with open(user_db_file) as jsonfile:
        jsondata = json.load(jsonfile)
        for user in jsondata.items():
            if user[1]["username"] == username:
                return user[0]
    
    raise ValueError("User not present in DB!", username)


def isUserRestricted(userid):

    with open(user_db_file) as jsonfile:
        jsondata = json.load(jsonfile)

        return jsondata[userid]["restricted"]

    return True

def checkPass(userid, password):
    with open(user_db_file) as jsonfile:
        jsondata = json.load(jsonfile)
        return jsondata[userid]["password"] == password

def generateID():
    # hash = os.urandom(16)
    hash = "%032x" % random.getrandbits(128)
    # print("hash value:", hash)
    return hash

def makeUser(username, password):
    if not os.path.exists("data"):
        os.mkdir("data")
    if not os.path.exists(user_db_file):
        with open(user_db_file, "w") as jsonfile:
            json.dump({}, jsonfile)

    try:
        getUserId(username)
    except ValueError:
        # user not present yet, all good
        pass
    else:
        # user already present
        raise ValueError("Username already exists!", username)

    jsondata = {}
    with open(user_db_file) as jsonfile:
        jsondata = json.load(jsonfile)

    userid = generateID()
    while(checkUser(userid)): # id already exists (what a chance!)
        userid = generateID() # generate a new one

    jsondata[userid] = {"username": username, "password": password, "restricted": True }


    with open(user_db_file, "w") as jsonfile:
        json.dump(jsondata, jsonfile)
    return userid

def checkUser(userid):
    with open(user_db_file) as jsonfile:
        jsondata = json.load(jsonfile)
        return userid in jsondata

def deleteUser(userid):
    jsondata = {}
    with open(user_db_file) as jsonfile:
        jsondata = json.load(jsonfile)

    if jsondata == {}:
        raise EOFError
        
    del jsondata[userid]

    with open(user_db_file, "w") as jsonfile:
        json.dump(jsondata, jsonfile)


def getLayer(userid, layername, dirname=None):
    import os.path

    # if not restricted, try globals first
    if not isUserRestricted(userid):
        filepath = "data/global/"
        if dirname:
            filepath += dirname +'/'
        filepath += layername
        filepath += ".json"

        if os.path.isfile(filepath):
            with open(filepath) as layerfile:
                return json.load(layerfile)

    # try users layers instead
    filepath = "data/user/"
    filepath += userid 
    filepath += "/"
    filepath += layername
    filepath += ".json"
    if os.path.isfile(filepath):
        with open(filepath) as layerfile:
            return json.load(layerfile)
    
    raise FileNotFoundError

def addLayer(userid,layername,data):
    filepath = "data/user/"
    filepath += userid 
    filepath += "/"
    if not os.path.exists(filepath):
        # make user directory
        os.makedirs(filepath)
    filepath += layername
    filepath += ".json"
    if os.path.exists(filepath):
        raise ValueError("layer already exists!")
    with open(filepath, "w") as layerfile:
        json.dump(data, layerfile)

def recurse_change(json, query_list, new_data):
    prop = query_list[0]
    query_list = query_list[1:]
    if prop.isdigit():
        prop = int(prop)
    if len(query_list) == 0:
        json[prop] = new_data
        return json
    else:
        json[prop] = recurse_change(json[prop],query_list,new_data)
        return json

def update_hash(userid, layername):
    if layername != "hashes":
        filepath = "data/user/"
        filepath += userid 
        filepath += "/"
        filepath += "hashes"
        filepath += ".json"
        if os.path.isfile(filepath):
            # hashes layer exists
            changeLayer(userid,"hashes", [layername], hash_state(userid, layername))
        else:
            # hashes layer does not exist yet
            addLayer(userid,"hashes", {layername : hash_state(userid, layername)})

def hash_state(userid, layername):
    data_state = getLayer(userid, layername)
    json_string = json.dumps(data_state)
    return hash(json_string)

def changeLayer(userid,layername,query,data):
    filepath = "data/user/"
    filepath += userid 
    filepath += "/"
    filepath += layername
    filepath += ".json"

    query = [q for q in query if q and q != ""]

    if os.path.isfile(filepath):
        # layer already exists

        if len(query) == 0:
            # overwrite whole file
            jsondata = data
        else:
            # only overwrite part
            jsondata = {}
            with open(filepath) as layerfile:
                jsondata =  json.load(layerfile)
            
            # update
            jsondata = recurse_change(jsondata,query,data)

        #write
        with open(filepath, "w") as layerfile:
            json.dump(jsondata, layerfile)
    else:
        # layer does not exist yet
        if len(query) > 0:
            raise ValueError("can't update non-existant layer!"+layername)
        addLayer(userid,layername,data)

    update_hash(userid, layername)
