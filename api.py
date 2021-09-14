import os
import datetime
import geopandas
import rtree  # needed for combining of layers
import json

from flask import Flask, request, abort
from flask_cors import CORS, cross_origin
from database_connector import makeUser, checkPass, getUserId, getLayer, changeLayer, checkUser, isUserRestricted
from abm_filters import apply_time_filters, apply_agent_filters

import time
import requests
from uuid import UUID, uuid4
import re
import asyncio


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
    log_dir = "data/logs/"
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
    except ValueError:
        abort(401)

    return {"user_id": userid, "restricted": restricted}


@app.route('/register', methods=['POST'])
def register():
    params = parseReq(request)
    username = params.get('username')
    password = params.get('password')
    if username == "":
        abort(400)
    try:
        userid = str(makeUser(username, password))
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


@app.route("/save_redis_result/", methods=['POST'])
def save_redis_result():
    params = request.json

    print("params received by save route %s " % params)
    userid = params["userid"]
    layername = params["layername"]
    task = params["task"]
    
    save_result_for_calculation_task(userid, layername, task)

    return "success"




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

    # trigger calculation for updated scenario and save results async
    if "scenario" in layername:
        try:
            print("trigger calculation ", layername)
            tasks_to_collect_results_for = trigger_calculation_for_scenario(userid, layername, data)
            print("tasks_to_collect_results_for %s " % tasks_to_collect_results_for)
            # TODO new route for this
            headers = {
            'Content-type': 'application/json',
            }
            for task in tasks_to_collect_results_for:
                # todo post to cityPyo itself
                payload = {
                    "userid": userid,
                    "layername": layername,
                    "task": task,
                }
                requests.post('http://localhost:5000/save_redis_result/', headers=headers, data=json.dumps(payload))
        except Exception as e:
            return "something went wrong {}".format(e)

    return "success"

# triggers a calculation in the computation services. returns tasks with result_uuids to collect results for.
def trigger_calculation_for_scenario(userid, layername, data) -> list:

    tasks_to_collect_results_for = []
    service_for_calculation_module = get_calculation_service_for_layername(layername)
    
    headers = {
        'Content-type': 'application/json',
    }

    print("this is the data obejct %s" % data)

    # forward request to calculation service api
    if service_for_calculation_module:
        data["city_pyo_user"] = userid
        print("forwarding these data %s to port %s " % (data, service_for_calculation_module))
        
        if "tasks" in list(data.keys()):  # trigger group task
            # post to grouptasks -> get back group result
            resp_json = requests.post('http://localhost:5003/grouptasks', headers=headers, data=json.dumps(data)).json()
            #resp_json = requests.post('http://' + service_for_calculation_module + ':5000/' + 'grouptasks', headers=headers, data=json.dumps(data)).json()
            
            # collect result for each task<->taskId
            for task_count, task in enumerate(data["tasks"]):
                task["result_uuid"] = resp_json["taskIds"][task_count]
                tasks_to_collect_results_for.append(task)
        
        else: # trigger single task        
            # todo if not wind: can only process group tasks
            if not service_for_calculation_module == "wind-api":
                raise NotImplementedError("single tasks only accepted by wind right now")

            resp_json = requests.post('http://' + 'localhost' + ':5003/' + 'windtask', headers=headers, data=json.dumps(data)).json()
            #resp_json = requests.post('http://' + service_for_calculation_module + ':5000/' + 'windtask', headers=headers, data=json.dumps(data)).json()
            task = data
            task["result_uuid"] = resp_json["taskId"]
            tasks_to_collect_results_for.append(task)
        
        return tasks_to_collect_results_for
    
    raise NotImplementedError("cannot find port for scenario ", layername)




def save_result_for_calculation_task(userid, layername, task):
    result = get_result_for_task(task["result_uuid"], layername)
    print("result of calc task %s " % result)

    # check if the result of this procsess is another grouptask id. ## this happens for wind
    try:
        grouptask_uuid = UUID(result)
        # set result of sub_group_task as task result
        print("getting sub group result")
        result = collect_results_for_sub_group_task(str(grouptask_uuid), userid, layername, task["result_uuid"])
    except:
        #  otherwise finally save result to disk
        pass

    hash = task["hash"]
    print("saving result :)")
    changeLayer(userid, get_result_layer_name(layername, hash), [], result)
    print("saved result :)")

  
# collects and returns the result of 1 task 
def get_result_for_task(task_id, layername):
    service = get_calculation_service_for_layername(layername)
    task_succeeded = False
    print("Listen for task-result. Result is the id of the GroupTask.")
    while not task_succeeded:
        response = requests.get('http://localhost:5003/tasks/{}'.format(task_id))
        print("task result id %s" % task_id)
        response_json = response.json()

        #response_json = requests.get('http://' + service + ':5000/tasks/{}'.format(task_id)).json()
        task_succeeded = response_json['taskSucceeded']
        time.sleep(1)

    return response_json["result"]
    

# returns results for group task
def collect_results_for_sub_group_task(group_task_id, userid, layername, task_id) -> list:
    service = get_calculation_service_for_layername(layername)

    print("group taks id %s" % group_task_id)
    are_results_completed = False
    completed_tasks_count = 0
    while not are_results_completed:
        response_json = requests.get('http://localhost:5003/grouptasks/{}'.format(group_task_id)).json()
        #response_json = requests.get('http://' + service + ':5000/tasks/{}'.format(task_id)).json()

        are_results_completed = response_json['grouptaskProcessed']  # boolean
        
        if response_json["tasksCompleted"] > completed_tasks_count and not are_results_completed:
            # update result layer, whenever a new result is coming in
            # todo save with "completed" property
            changeLayer(userid, get_result_layer_name(layername, hash), [], response_json["results"]) # results is array of all results

        print("tasks completed: %s" % response_json["tasksCompleted"])
        time.sleep(1)
    

    return response_json["results"]


def get_result_layer_name(layername, hash) -> str:
    result_layer_name = layername + "_" + hash
    if layername.startswith('_scenario'):
        result_layer_name = re.sub("\_scenario$", '', layername)

    return result_layer_name 


def get_calculation_service_for_layername(layername):
    service_for_calculation_module = None

    if "wind" in layername:
        service_for_calculation_module = 'wind-api'  
    if "water" in layername:
        service_for_calculation_module = 'swimdock-api'
    if "noise" in layername:
        service_for_calculation_module = 'noise-api'

    return service_for_calculation_module


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
