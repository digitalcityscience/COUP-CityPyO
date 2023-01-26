"""
area_planning_type
land_use_detailed_type
land_use_suggested

upperfloor + groundfloor

missing buildings ['G01', 'G52', 'G42']
"""

import json
#import geopandas


if __name__ == "__main__":


    with open("buildings_0303.json") as jsonfile:
        table_data = json.load(jsonfile)
    with open("groundfloor.json") as jsonfile:
        groundfloor = json.load(jsonfile)
    with open("upperfloor.json") as jsonfile:
        upperfloor = json.load(jsonfile)

    
    """
    missing_buildings = []

    for feature in table_data["features"]:
        building_id = feature["properties"]["building_id"]
        building_updated = False
        for upperfloor_feature in upperfloor["features"]:
            if building_id == upperfloor_feature["properties"]["building_id"]:
                print("updating building", building_id)
                feature["properties"]["area_planning_type"] = upperfloor_feature["properties"]["area_planning_type"]
                feature["properties"]["land_use_detailed_type"] = upperfloor_feature["properties"]["land_use_detailed_type"]
                feature["properties"]["land_use_suggested"] = upperfloor_feature["properties"]["land_use_suggested"]
                building_updated = True
        if not building_updated:
            missing_buildings.append(building_id)

    print("missing buildings normal", missing_buildings)

    
    with open("new_table_.json", "w") as jsonfile:
        json.dump(table_data, jsonfile)
        jsonfile.close()

    """ 
    #combine groundfloor and upperfloor

    missing_buildings_upper = []
    missing_buildings_ground = []

    for feature in table_data["features"]:
        building_id = feature["properties"]["building_id"]
        feature["properties"]["upperfloor"] = {}
        feature["properties"]["groundfloor"] = {}
        building_updated_upper = False
        building_updated_lower = False

        for upperfloor_feature in upperfloor["features"]:
            
            if building_id == upperfloor_feature["properties"]["building_id"]:
                feature["properties"]["upperfloor"]["area_planning_type"] = upperfloor_feature["properties"]["area_planning_type"]
                feature["properties"]["upperfloor"]["land_use_detailed_type"] = upperfloor_feature["properties"]["land_use_detailed_type"]
                feature["properties"]["upperfloor"]["land_use_suggested"] = upperfloor_feature["properties"]["land_use_suggested"]
                
                print(feature["properties"]["upperfloor"])
                building_updated_upper = True
        if not building_updated_upper:
            missing_buildings_upper.append(building_id)


        for groundfloor_feature in groundfloor["features"]:
            if building_id == groundfloor_feature["properties"]["building_id"]:
                feature["properties"]["groundfloor"]["area_planning_type"] = groundfloor_feature["properties"]["area_planning_type"]
                feature["properties"]["groundfloor"]["land_use_detailed_type"] = groundfloor_feature["properties"]["land_use_detailed_type"]
                feature["properties"]["groundfloor"]["land_use_suggested"] = groundfloor_feature["properties"]["land_use_suggested"]
                building_updated_lower = True
        if not building_updated_lower:
            missing_buildings_ground.append(building_id)

        del feature["properties"]["area_planning_type"]
        del feature["properties"]["land_use_detailed_type"]
        del feature["properties"]["land_use_suggested"]

    
    print("missing buildings ground", missing_buildings_ground)
    print("missing buildings upper", missing_buildings_upper)

    
    with open("new_table_ground_and_upper.json", "w") as jsonfile:
        json.dump(table_data, jsonfile)
        jsonfile.close()

    
    """

    with open("new_table.json") as jsonfile:
        new_table = json.load(jsonfile)
    
    with open("new_table_ground_and_upper.json") as jsonfile:
            new_table_more = json.load(jsonfile)

        
    with open("designable_area_half_table.json") as jsonfile:
            boundaries = json.load(jsonfile)

    
    new_table_gdf = geopandas.read_file("new_table.json", driver="GeoJSON")
    new_table_gdf = new_table_gdf.set_crs("EPSG:4326", allow_override=True)

    new_table_more_gdf = geopandas.read_file("new_table_ground_and_upper.json", driver="GeoJSON")
    new_table_more_gdf = new_table_more_gdf.set_crs("EPSG:4326", allow_override=True)

    bounds_gdf = geopandas.read_file("designable_area_half_table.json", driver="GeoJSON")
    bounds_gdf = bounds_gdf.set_crs("EPSG:25832")
    bounds_gdf = bounds_gdf.to_crs("EPSG:4326")

    new_table_gdf = geopandas.clip(new_table_gdf, bounds_gdf)
    new_table_more_gdf = geopandas.clip(new_table_more_gdf, bounds_gdf)

    new_table_gdf.to_file("new_table_clipped.json", driver="GeoJSON")
    new_table_more_gdf.to_file("new_table_more_clipped.json", driver="GeoJSON")
    """