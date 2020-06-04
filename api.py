from flask import Flask, request, abort
from database_connector import makeUser,checkPass,getUserId,getLayer,changeLayer

app = Flask(__name__)

def parseReq(request):
    if request.method == 'POST':
        params = dict(request.json)
    elif request.method == "GET":
        params = {}
        for key in request.args.keys():
            # we have to parse this element by element, to detect duplicate keys
            if len(request.args.getlist(key)) > 1:
                params[key] = request.args.getlist(key) # duplicate key, store all values as list
            else:
                params[key] = request.args[key] # default behaviour: store single value
    else:
        abort(400)
    
    if params and len(params.items()) > 0:
        return params
    else:
        return {}

@app.route('/test')
def test():
    params = parseReq(request)
    return params

@app.route('/login', methods = ['POST'])
def login():
    params = parseReq(request)
    if not params:
        abort(400)
    username = params.get('username')
    password = params.get('password')
    if username == "":
        abort(400)
    try:
        userid = str(getUserId(username))
        if not checkPass(userid, password):
            abort(401)
    except ValueError:
            abort(401)

    return { "user_id": userid }

@app.route('/register', methods = ['POST'])
def register():
    params = parseReq(request)
    username = params.get('username')
    password = params.get('password')
    if username == "":
        abort(400)
    try:
        userid = str(makeUser(username,password))
    except ValueError:
        abort(403) # username already exists

    return { "user_id": userid }

@app.route('/')
def index():
    return "Hi :)"

@app.route("/getLayer", methods = ['GET'])
@app.route("/getLayer/", methods = ['GET'])
def getLayerRoute():
    params = request.json
    layer = params.get("layer")
    userid = params.get("userid")
    try:
        return getLayer(userid,layer)
    except FileNotFoundError as e:
        print("/getLayer",params)
        print(e)
        abort(400)
        
@app.route("/getLayer/<path:query>", methods = ['GET'])
def getLayerData(query):
    params = request.json
    layer = params.get("layer")
    userid = params.get("userid")
    try:
        json = getLayer(userid,layer)
    except FileNotFoundError as e:
        print("/getLayer/"+query,params)
        print(e)
        abort(400)

    data = json
    props = query.split("/")
    for prop in props:
        if len(prop) is 0:
            continue
        if prop.isdigit():
            prop = int(prop)
        data = data[prop]
    return {"data": data}

@app.route("/addLayerData/<path:query>", methods = ['POST'])
def addLayerData(query):
    params = request.json
    userid = params.get("userid")
    data = params.get("data")
    layername, *props = query.split("/")

    try:
        changeLayer(userid,layername,props,data)
    except Exception as e:
        print("/addLayerData/"+query,params)
        print(e)
        abort(400)

    return "success"

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")