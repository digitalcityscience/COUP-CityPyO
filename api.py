import os
import datetime
import geopandas
import rtree  # needed for combining of layers
import json

from flask import Flask, request, abort
from flask_cors import CORS, cross_origin
from flask_compress import Compress

from database_connector import getUserContext, makeUser, checkPass, getUserId, getLayer, changeLayer, checkUser, isUserRestricted
from abm_filters import apply_time_filters, apply_agent_filters


app = Flask(__name__)
CORS(app)
Compress(app)
app.config['CORS_HEADERS'] = 'Content-Type'
log_dir = "data/logs/"


def parseReq(request):
    if request.method == 'POST':
        params = dict(request.json)
    elif request.method == "GET":
        params = {}
        for key in request.args.keys():
            # we have to parse this element by element, to detect duplicate keys
            if len(request.args.getlist(key)) > 1:
                params[key] = request.args.getlist(key)  # duplicate key, store all values as list
            else:
                params[key] = request.args[key]  # default behaviour: store single value
    else:
        abort(400)

    if params and len(params.items()) > 0:
        return params
    else:
        return {}


def log_login_request(username):
    filepath = log_dir + "login_requests.csv"

    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)

    if not os.path.isfile(filepath):
        # create file with headers
        with open(filepath, "w") as log_file:
            log_file.write("timestamp, username")

    with open(filepath, "a") as log_file:
        # add login request
        log_file.write("\n" + str(datetime.datetime.now()) + "," + username)


# logs a request performed to the AIT, in order to keep track of how many requests we sent there
def log_ait_calc_request(data: dict):

    filepath = log_dir + "ait_calc_requests" + ".csv"

    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)

    if not os.path.isfile(filepath):
        with open(filepath, "w") as log_file:
            # create file with headers
            log_file.write("timestamp, calc_type, result_uuid, target_url")

    with open(filepath, "a") as log_file:
        # add login request
        log_file.write(
            "\n"
            + data["timestamp"] + ","
            + data["calc_type"] + ","
            + data["result_uuid"] + ","
            + data["target_url"]
        )


@app.route('/')
def index():
    return "Hi :)"


@app.route('/test')
def test():
    params = parseReq(request)
    return params


@app.route('/login', methods=['POST'])
def login():
    params = parseReq(request)
    if not params:
        abort(400)
    username = params.get('username')
    password = params.get('password')
    log_this_request = params.get('log_this_request')

    if log_this_request:
        log_login_request(username)

    if username == "":
        abort(400)
    try:
        userid = str(getUserId(username))
        if not checkPass(userid, password):
            abort(401)
        restricted = isUserRestricted(userid)
        context = getUserContext(userid)
    except ValueError:
        abort(401)

    return {"user_id": userid, "restricted": restricted, "context": context}


@app.route('/register', methods=['POST'])
def register():
    params = parseReq(request)
    username = params.get('username')
    password = params.get('password')
    context = params.get('context')
    if username == "":
        abort(400)
    try:
        userid = str(makeUser(username, password, context))
    except ValueError:
        abort(403)  # username already exists

    return {"user_id": userid}

@app.route("/getLayer", methods=['POST', 'GET'])
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
        abort(404)


@app.route("/getLayer/<path:query>", methods=['POST'])
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
            abort(404)

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
    time_filters = params.get("time_filters")  # todo: only works while request is post

    try:
        scenario_list = getLayer(userid, "abmScenarios")
    except FileNotFoundError as e:
        print("/getLayer/" + query, params)
        print(e)
        abort(404)

    abm_result = None
    scenario_name = None
    for scenario_name, scenario_props in scenario_list.items():
        print(scenario_name, scenario_props)
        if scenario_props == requested_scenario_props:
            try:
                abm_result = getLayer(userid, scenario_name, "abm")
                break
            except FileNotFoundError as e:
                print("/getLayer/" + query, params)
                print(e)
                abort(404)

    if not abm_result:
        print("no abm result found")
        abort(404)  # no matching result found

    if time_filters:
        apply_time_filters(abm_result, time_filters)

    if agent_filters:
        apply_agent_filters(abm_result, agent_filters)

    return {"data": abm_result["data"], "scenario_name": scenario_name}


@app.route("/addLayerData/<path:query>", methods=['POST'])
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

@app.route("/logCalcRequestAIT/", methods=['POST'])
def addLogDataRoute():
    params = request.json
    
    try:
        log_ait_calc_request(params)
    except Exception as e:
        print("/logCalcRequestAIT/", params)
        print(e)
        abort(400)
        
    return "success"


@app.route("/combineLayers", methods=['POST'])
def combineLayersRoute():
    params = request.json
    userid = params.get("userid")
    layer_1 = params.get("layer_1")
    layer_2 = params.get("layer_2")

    print(layer_1)

    if not checkUser(userid):
        abort(401)

    try:
        return combineLayers(layer_1, layer_2)
    except Exception as e:
        print("combine Layers did not work")
        print(e)
        abort(400)


def combineLayers(layer_1, layer_2):

    # make geodataframe from first layer
    layer_1_gdf = geopandas.GeoDataFrame.from_features(
        layer_1["features"],
        crs="urn:ogc:def:crs:EPSG::4326"
    )
    # make geodataframe from second layer
    layer_2_gdf = geopandas.GeoDataFrame.from_features(
        layer_2["features"],
        crs="urn:ogc:def:crs:EPSG::4326"
    )

    # combine geodataframes by intersection overlay
    combinedLayer = geopandas.overlay(layer_1_gdf, layer_2_gdf, how="intersection", keep_geom_type=False)

    # add new property "meanScaledValue" - the average of both dataframes values.
    combinedLayer.loc[:, 'meanScaledValue'] = (combinedLayer['scaledValue_1'] + combinedLayer['scaledValue_2']) / 2

    # export to geojson
    geojson = combinedLayer.to_json()

    print(len(combinedLayer.index))

    return json.loads(geojson)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
