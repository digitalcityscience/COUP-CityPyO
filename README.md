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
