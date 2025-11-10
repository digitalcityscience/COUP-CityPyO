# CityPyO
Kommen Sie nicht zum arbeiten? Ärgern Sie sich auch, dass cityIO ständig down ist?

Das hat endlich ein Ende! Mit _CityPyO_! (Bei Risiken und Nebenwirkungen fragen Sie Ihren Systemadministrator)

## Installation

``` $ pip install -r requirements.txt ```

## Testing

Run a development server with:

``` $ python3 api.py ```

Run integration tests with:

``` $ python3 test_full.py ```

You can also use `pytest`, but it will not clean up after itself and you'll have to delete test data manually afterwards.

## API endpoints:

* `/login`, POST, request body: _username_, _password_, returns _user_id_ on success
* `/register`, POST,  request body: _username_, _password_, returns _user_id_ on success
* `/getLayer/<path>`, GET, request body: _userid_, _layer_, returns the data at specified _path_ (slash delimited) for layer with name _layer_
* `/addLayerData/<path>`, POST, request body: _userid_, _data_, sets the data at specified _path_. Layer name is the entry before the first slah in _path_. If the layer does not exist yet, trying to set a nested path will fail.


## COUP SETUP
Files needed for COUP that are stored in CityPyO

### Buildings
Provide a groundfloor.json, upperfloor.json and rooftop.json and buildings.json in data/user/YOUR_ID 
Each file should contain the respective geometries. The buildings.json represents the main footprint geometries to be used in the wind and noise simulation and the total building height.

Following properties can provided per Feature. Mandatory for the visualization to work are city_scope_id and land_use_detailed_type. Upperfloor features must contain a float value for building_height Rooftop features must contain float values for building_height and additional_roof_height

{"building_id": "G03", "land_use_detailed_type": "residential", "building_height": 44.3, "additional_roof_height": 47.5, "area_planning_type": "building", "floor_area": 341.8590000002878, "city_scope_id": "B-03-1"}


### OpenSpaces

The open spaces displayed are read from a spaces.json provided by your CityPyo user. Following properties can provided per Feature. Mandatory for the visualization to work are city_scope_id and land_use_detailed_type.

"properties": {"area_planning_type": "specialUseArea", "land_use_general_type": "privateOS", "land_use_detailed_type": "schoolOutdoorArea", "floor_area": 2774.420039495546, "city_scope_id": "S-283"}

### Static simulation result files
Put your abm results as produced by the COUP-ABM simulation in the data/user/YOUR_ID/abm 
Sun result is currently a static file as sun_exposure.json. Sun result can be retrieved like the wind-results from AIT.

