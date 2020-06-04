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

    if jsondata == {}:
        raise EOFError

    userid = generateID()
    while(checkUser(userid)): # id already exists (what a chance!)
        userid = generateID() # generate a new one
        
    jsondata[userid] = {"username": username, "passwort": password }

    
    if jsondata == {}:
        raise EOFError

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

# def getUserData(username):
#     dbentry = readCSVbyKey("users_db.csv", username)
#     if not dbentry:# or len(dbentry) < 3:
#         raise ValueError("this user was not found or has no data!")
#     if len(dbentry) < 3:
#         return {}
#     return json.loads(dbentry[2])

# def setUserData(userid, userdata):
#     if checkUser(userid): # user exists
#         del userdata["username"] # anonymisation :P

#         # delete all empty and null values from userdata
#         userdata = {k: v for k, v in userdata.items() if v is not None and v is not ""}

#         file = "users_db.csv"
#         rows = []
#         username = ""
#         with open(file, 'r') as csvfile:
#             reader = csv.reader(csvfile, delimiter=',', quotechar='\'') # use ' as quotechar, since json string representation uses "
#             for row in reader:
#                 if row[1] != userid:
#                     rows.append(row)
#                 else: # this row will be overwritten
#                     username = row[0]
#         with open(file, 'w', newline='') as csvfile: # newline '' prohibits stupid windows CR
#             csvwriter = csv.writer(csvfile, delimiter=',', quotechar='\'', quoting=csv.QUOTE_MINIMAL) # use ' as quotechar, since json string representation uses "
#             csvwriter.writerows(rows)
#             csvwriter.writerow([username,userid,json.dumps(userdata)])

#     else:
#         raise ValueError("this user id was not found!")

# def getTimeStamp():
#     return datetime.datetime.today()

# def appendData(userid, data):
#     file = "data_db.csv"
#     numLines = None
#     with open(file, 'r') as csvfile:
#         lines = csv.reader(csvfile, delimiter=',')
#         numLines = len(list(lines)) # get the current number of entries for use as an id

#     with open(file, 'a', newline='') as csvfile:
#         csvwriter = csv.writer(csvfile, delimiter=',',
#                                 quotechar='\'', quoting=csv.QUOTE_MINIMAL) # use ' as quotechar, since json string representation uses "

#         timestamp = getTimeStamp()
#         if data.get("yesterday"): # someone forgot, huh?
#             # set to latest second of yesterday, so this will be the most recent entry of yesterday
#             timestamp -= datetime.timedelta(days=1)
#             timestamp = timestamp.replace(hour=23,minute=59,second=59,microsecond=999999)
#         newEntry = [numLines, timestamp, userid, json.dumps(data) ]
#         csvwriter.writerow(newEntry)

# def getFullDumpStr():
#     file = "data_db.csv"
#     output = ""
#     with open(file, 'r') as csvfile:
#         reader = csv.reader(csvfile, delimiter=',', quotechar='\'') # use ' as quotechar, since json string representation uses "
#         for line in reader:
#             output += str(line) + "\n"
#     return output

# def getFullDumpJSON():
#     file = "data_db.csv"
#     output = []
#     with open(file, 'r') as csvfile:
#         reader = csv.DictReader(csvfile, delimiter=',', quotechar='\'') # use ' as quotechar, since json string representation uses "
#         for line in reader:
#             output.append(dict(line))
#     return output
