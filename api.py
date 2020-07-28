from flask import Flask, request, abort
from flask_cors import CORS
from database_connector import makeUser,checkPass,getUserId,getLayer,changeLayer,checkUser

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

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

@app.route('/')
def index():
    return "Hi :)"

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
        userid = str(makeUser(username, password))
    except ValueError:
        abort(403) # username already exists

    return { "user_id": userid }

@app.route("/getLayer", methods = ['POST', 'GET'])
# @app.route("/getLayer/", methods = ['POST'])
def getLayerRoute():
    print(request)
    params = request.json
    layer = params.get("layer")
    userid = params.get("userid")

    if not checkUser(userid):
        abort(401)

    try:
        return getLayer(userid, layer)
    except FileNotFoundError as e:
        print("/getLayer", params)
        print(e)
        abort(400)
        
@app.route("/getLayer/<path:query>", methods = ['POST'])
def getLayerData(query):
    params = request.json
    layer = params.get("layer")
    userid = params.get("userid")

    if not checkUser(userid):
        abort(401)

    if query == "abmScenario":
        return getAbmData(query)
    else:
        try:
            json = getLayer(userid, layer)
        except FileNotFoundError as e:
            print("/getLayer/" + query, params)
            print(e)
            abort(400)

        data = json
        props = query.split("/")
        for prop in props:
            if len(prop) == 0:
                continue
            if prop.isdigit():
                prop = int(prop)
            data = data[prop]

        return {"data": data}


def getAbmData(query):
    params = request.json
    userid = params.get("userid")
    requested_scenario_props = params.get("scenario_properties")  # todo: only works while request is post
    agent_filters = params.get("agent_filters")  # todo: only works while request is post

    try:
        scenario_list = getLayer(userid, "abmScenarios")
    except FileNotFoundError as e:
        print("/getLayer/" + query, params)
        print(e)
        abort(400)

    abm_result = None
    print(requested_scenario_props)
    for scenario_name, scenario_props in scenario_list.items():
        print(scenario_name, scenario_props)
        if scenario_props == requested_scenario_props:
            try:
                abm_result = getLayer(userid, scenario_name, "abm")
            except FileNotFoundError as e:
                print("/getLayer/" + query, params)
                print(e)
                abort(404)

    if not abm_result:
        print("no abm result found")
        abort(404)  # no matching result found

    if agent_filters:
        relevant_agents_data = []
        for agent_data in abm_result["data"]:
            relevant_agent = True
            for key, value in agent_filters.items():
                try:
                    if not agent_data["agent"][key] == value:
                        relevant_agent = False
                        break
                except Exception as e:
                    print("filter criteria does not match target data")
                    print(e)
                    abort(400)
            if relevant_agent:
                relevant_agents_data.append(agent_data)

        return {"data": relevant_agents_data}

    else:  # return the entire result dataset, if no filters applied
        return {"data": abm_result["data"]}


@app.route("/addLayerData/<path:query>", methods = ['POST'])
def addLayerData(query):
    params = request.json
    userid = params.get("userid")
    data = params.get("data")
    layername, *props = query.split("/")

    if not checkUser(userid):
        abort(401)

    try:
        changeLayer(userid, layername, props, data)
    except Exception as e:
        print("/addLayerData/" + query, params)
        print(e)
        abort(400)

    return "success"

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")