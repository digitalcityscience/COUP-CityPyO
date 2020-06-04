from flask import Flask, request, abort
from database_connector import makeUser,checkPass,getUserId

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
    print(request.json)
    params = request.json
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

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")