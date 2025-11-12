import json
import geopandas


def get_invalid_geometries(gdf) -> geopandas.GeoDataFrame | None: 
    gdf["valid_geometry"] = gdf["geometry"].is_valid == True
    invalid_features = gdf[gdf["valid_geometry"] == False]
    
    if len(invalid_features.length) > 0:
        return invalid_features
    
    return geopandas.GeoDataFrame()


def fix_geoms_by_buffer_0(gdf: geopandas.GeoDataFrame) -> geopandas.GeoDataFrame:
    gdf.geometry = gdf.geometry.buffer(0)

    return gdf

def ensure_valid_geojson(jsondata: dict) -> dict:
    try:
        # try creating a geodataframe from the data
        gdf = geopandas.GeoDataFrame.from_features(jsondata["features"])
    except Exception as e:
        message = str(e)
        print(message)
        if 'geometry' in message:
            raise ValueError("Invalid GeoJSON missing 'geometry' info in features")
        elif 'properties' in message:
            raise ValueError("Invalid GeoJSON missing 'properties' info in features")
        else:
            raise ValueError("Invalid GeoJSON provided", e)

    invalids_gdf = get_invalid_geometries(gdf)
    if len(invalids_gdf):
        gdf = fix_geoms_by_buffer_0(gdf)
        # check again
        if len(get_invalid_geometries(gdf)):
            raise ValueError(f"Invalid geometries provided : {json.loads(invalids_gdf.to_json())}")
        
    # convert back to dict
    return json.loads(gdf.to_json())
    
