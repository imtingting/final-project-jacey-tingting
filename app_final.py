# MUSA 509
# Final Project
# Tingting Huang, Jacey Chang
import io
import json
import logging
import random

from flask import Flask, Response, render_template, escape, request, url_for
import requests
from sqlalchemy import create_engine, String, Integer
from sqlalchemy.sql import text, bindparam
from google.cloud import bigquery
import geopandas as gpd
from shapely.geometry import shape
from datetime import datetime
from cartoframes.viz import Layer, Map, color_category_style, popup_element

from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import CSSResources, JSResources
from shapely import wkt

bokeh_css = CSSResources(mode="cdn", version="2.2.3", minified=True)
bokeh_js = JSResources(mode="cdn", version="2.2.3", minified=True)

app = Flask(__name__, template_folder="templates")

bqclient = bigquery.Client.from_service_account_json("Musa509-Lab5-42148b13cb70.json")

#load credentials from a file
with open("pg-credentials.json", "r") as f_in:
   pg_creds = json.load(f_in)

# mapbox
with open("mapbox_token.json", "r") as mb_token:
    MAPBOX_TOKEN = json.load(mb_token)["token"]

# load credentials from JSON file
HOST = pg_creds["HOST"]
USERNAME = pg_creds["USERNAME"]
PASSWORD = pg_creds["PASSWORD"]
DATABASE = pg_creds["DATABASE"]
PORT = pg_creds["PORT"]
engine = create_engine(f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

class UserInput():
    address="Meyerson Hall, Philadelphia"
    lng=-75.19
    lat=39.95

user_input=UserInput()

# index page
@app.route("/")
def index():
    """Index page"""
    return render_template("index.html")

# Basic information
def get_basic_condition(lng, lat):
    job_config_census = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("lng", "FLOAT", lng),
        bigquery.ScalarQueryParameter("lat", "FLOAT", lat),
        ]
    )
    query_census = f"""
         SELECT a.geo_id, total_pop, Round((white_pop/total_pop)*100, 2) as white_pop_pct, Round((black_pop/total_pop)*100, 2) as black_pop_pct,
         Round((asian_pop/total_pop)*100, 2) as asian_pop_pct, Round((hispanic_pop/total_pop)*100, 2) as hispanic_pop_pct, median_age, gini_index,
         Round((poverty/total_pop)*100, 2) as poverty_rate, median_income, internal_point_lat, internal_point_lon, internal_point_geo, tract_geom,
         median_rent, owner_occupied_housing_units_median_value as median_housing_value
         FROM bigquery-public-data.census_bureau_acs.censustract_2018_5yr as a
         LEFT JOIN
         (SELECT geo_id, internal_point_lat, internal_point_lon, internal_point_geo, tract_geom
         FROM bigquery-public-data.geo_census_tracts.us_census_tracts_national) as b
         ON a.geo_id = b.geo_id
         WHERE ST_Intersects(tract_geom, ST_GeogPoint(@lng, @lat))
    """
    census_data = [dict(row) for row in bqclient.query(query_census, job_config=job_config_census).result()]

    return census_data[0]

# Get the census tracts that within 2000 meters
def get_geo_tract(lng, lat):
    job_config_tract = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("lng", "FLOAT", lng),
        bigquery.ScalarQueryParameter("lat", "FLOAT", lat),
        ]
    )
    query_geo_tract = f"""
         SELECT a.geo_id, total_pop, Round((white_pop/total_pop)*100, 2) as white_pop_pct, Round((black_pop/total_pop)*100, 2) as black_pop_pct,
         Round((asian_pop/total_pop)*100, 2) as asian_pop_pct, Round((hispanic_pop/total_pop)*100, 2) as hispanic_pop_pct, median_age, gini_index,
         Round((poverty/total_pop)*100, 2) as poverty_rate, median_income,tract_geom,
         ST_Distance(ST_GeogPoint(@lng, @lat), internal_point_geo) as distance_away_meters,
         FROM bigquery-public-data.census_bureau_acs.censustract_2018_5yr as a
         LEFT JOIN
         (SELECT geo_id, internal_point_lat, internal_point_lon, internal_point_geo, tract_geom
         FROM bigquery-public-data.geo_census_tracts.us_census_tracts_national) as b
         ON a.geo_id = b.geo_id
         WHERE ST_Distance(ST_GeogPoint(@lng, @lat), internal_point_geo) < 2000
    """
    df = bqclient.query(query_geo_tract, job_config=job_config_tract).to_dataframe()
    df['tract_geom'] = df['tract_geom'].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry='tract_geom')
    return gdf


# Get address and report information
@app.route("/info/", methods=["GET"])
def get_info():
    address = request.args.get("address")
    if address is None:
        user_input.address="Meyerson Hall, Philadelphia"
        return f"""
        <p>No address specified, try:</p>
        <div>
        <a href="{url_for('info', address='Meyerson Hall, University of Pennsylvania')}">{url_for('info', address='Meyerson Hall, University of Pennsylvania')}</a>
        </div>
        """
    user_input.address=address
    geocoding_call = (
        "https://api.mapbox.com/geocoding/v5/mapbox.places/"
        f"{address}.json?access_token={MAPBOX_TOKEN}"
    )
    resp = requests.get(geocoding_call)
    lng, lat = resp.json()["features"][0]["center"]
    user_input.lng=lng
    user_input.lat=lat

# Amenity
    job_config_market = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("poi_category", "STRING", "convenience"),
            bigquery.ScalarQueryParameter("lng", "FLOAT", lng),
            bigquery.ScalarQueryParameter("lat", "FLOAT", lat),
        ]
    )
    query_market = f"""
        SELECT (select value from unnest(all_tags) WHERE key = 'name') as shop_name,
               (select value from unnest(all_tags) WHERE key = 'shop') as shop_type,
               (select value from unnest(all_tags) WHERE key = 'addr:street') as address,
               (select value from unnest(all_tags) WHERE key = 'phone') as phone_number,
               CAST(round(ST_Distance(ST_GeogPoint(@lng, @lat), ST_Centroid(geometry))) AS int64) as distance_away_meters,
               ST_X(ST_Centroid(geometry)) as longitude,
               ST_Y(ST_Centroid(geometry)) as latitude
          FROM `bigquery-public-data.geo_openstreetmap.planet_features`
         WHERE ('shop', @poi_category) IN (SELECT (key, value) FROM UNNEST(all_tags))
         ORDER BY distance_away_meters ASC
         LIMIT 5
    """

    nearest_market = [dict(row) for row in bqclient.query(query_market, job_config=job_config_market).result()]

# Fast-food
    job_config_fast_food = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("poi_category", "STRING", "fast_food"),
            bigquery.ScalarQueryParameter("lng", "FLOAT", lng),
            bigquery.ScalarQueryParameter("lat", "FLOAT", lat),
        ]
    )
    query_fast_food = f"""
        SELECT (select value from unnest(all_tags) WHERE key = 'name') as amenity_name,
               (select value from unnest(all_tags) WHERE key = 'amenity') as amenity_type,
               (select value from unnest(all_tags) WHERE key = 'addr:street') as address,
               (select value from unnest(all_tags) WHERE key = 'phone') as phone_number,
               CAST(round(ST_Distance(ST_GeogPoint(@lng, @lat), ST_Centroid(geometry))) AS int64) as distance_away_meters,
               ST_X(ST_Centroid(geometry)) as longitude,
               ST_Y(ST_Centroid(geometry)) as latitude
          FROM `bigquery-public-data.geo_openstreetmap.planet_features`
         WHERE ('amenity', @poi_category) IN (SELECT (key, value) FROM UNNEST(all_tags))
         ORDER BY distance_away_meters ASC
         LIMIT 5
    """
    nearest_fast_food = [dict(row) for row in bqclient.query(query_fast_food, job_config=job_config_fast_food).result()]


# Supermarket
    job_config_supermarket = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("poi_category", "STRING", "supermarket"),
            bigquery.ScalarQueryParameter("lng", "FLOAT", lng),
            bigquery.ScalarQueryParameter("lat", "FLOAT", lat),
        ]
    )
    query_supermarket = f"""
        SELECT (select value from unnest(all_tags) WHERE key = 'name') as shop_name,
               (select value from unnest(all_tags) WHERE key = 'shop') as shop_type,
               (select value from unnest(all_tags) WHERE key = 'addr:street') as address,
               (select value from unnest(all_tags) WHERE key = 'phone') as phone_number,
               CAST(round(ST_Distance(ST_GeogPoint(@lng, @lat), ST_Centroid(geometry))) AS int64) as distance_away_meters,
               ST_X(ST_Centroid(geometry)) as longitude,
               ST_Y(ST_Centroid(geometry)) as latitude
          FROM `bigquery-public-data.geo_openstreetmap.planet_features`
         WHERE ('shop', @poi_category) IN (SELECT (key, value) FROM UNNEST(all_tags))
         ORDER BY distance_away_meters ASC
         LIMIT 5
    """
    nearest_supermarket = [dict(row) for row in bqclient.query(query_supermarket, job_config=job_config_supermarket).result()]

# Basic information
    curr_time = datetime.now().strftime("%B %d, %Y %I:%M %p")
    census_data = get_basic_condition(lng, lat)
    tract_gdf = get_geo_tract(lng, lat)


# Html
# Html_content
    html_content= render_template(
        "Content.html",
        address=address,
        curr_time=curr_time,
        white_pop_pct = census_data['white_pop_pct'],
        black_pop_pct = census_data['black_pop_pct'],
        asian_pop_pct = census_data['asian_pop_pct'],
        hispanic_pop_pct = census_data['hispanic_pop_pct'],
        gini_index = census_data['gini_index'],
        poverty_rate = census_data['poverty_rate'],
        median_age = census_data['median_age'],
        median_rent = census_data['median_rent'],
        median_housing_value = census_data['median_housing_value'],
        nearest_market1 = nearest_market[0]['shop_name'],
        nearest_market2 = nearest_market[1]['shop_name'],
        nearest_market3 = nearest_market[2]['shop_name'],
        distance_market1 = nearest_market[0]['distance_away_meters'],
        distance_market2 = nearest_market[1]['distance_away_meters'],
        distance_market3 = nearest_market[2]['distance_away_meters'],
        nearest_fast_food1 = nearest_fast_food[0]['amenity_name'],
        nearest_fast_food2 = nearest_fast_food[1]['amenity_name'],
        nearest_fast_food3 = nearest_fast_food[2]['amenity_name'],
        distance_fast_food1 = nearest_fast_food[0]['distance_away_meters'],
        distance_fast_food2 = nearest_fast_food[1]['distance_away_meters'],
        distance_fast_food3 = nearest_fast_food[2]['distance_away_meters'],
        nearest_supermarket1 = nearest_supermarket[0]['shop_name'],
        nearest_supermarket2 = nearest_supermarket[1]['shop_name'],
        nearest_supermarket3 = nearest_supermarket[2]['shop_name'],
        distance_supermarket1 = nearest_supermarket[0]['distance_away_meters'],
        distance_supermarket2 = nearest_supermarket[1]['distance_away_meters'],
        distance_supermarket3 = nearest_supermarket[2]['distance_away_meters']
        )

# Html_map_poi
    html_map_poi = render_template(
                "POI_map.html",
                mapbox_token=MAPBOX_TOKEN,
                center_lng= lng,
                center_lat= lat,
                market1_lng = nearest_market[0]['longitude'],
                market2_lng = nearest_market[1]['longitude'],
                market3_lng = nearest_market[2]['longitude'],
                market1_lat = nearest_market[0]['latitude'],
                market2_lat = nearest_market[1]['latitude'],
                market3_lat = nearest_market[2]['latitude'],
                market1_name = nearest_market[0]['shop_name'],
                market2_name = nearest_market[1]['shop_name'],
                market3_name = nearest_market[2]['shop_name'],
                market1_phone = nearest_market[0]['phone_number'],
                market2_phone = nearest_market[1]['phone_number'],
                market3_phone = nearest_market[2]['phone_number'],                
                fast_food1_lng = nearest_fast_food[0]['longitude'],
                fast_food2_lng = nearest_fast_food[1]['longitude'],
                fast_food3_lng = nearest_fast_food[2]['longitude'],
                fast_food1_lat = nearest_fast_food[0]['latitude'],
                fast_food2_lat = nearest_fast_food[1]['latitude'],
                fast_food3_lat = nearest_fast_food[2]['latitude'],
                fast_food1_name = nearest_fast_food[0]['amenity_name'],
                fast_food2_name = nearest_fast_food[1]['amenity_name'],
                fast_food3_name = nearest_fast_food[2]['amenity_name'],
                fast_food1_phone = nearest_fast_food[0]['phone_number'],
                fast_food2_phone = nearest_fast_food[1]['phone_number'],
                fast_food3_phone = nearest_fast_food[2]['phone_number'],  
                supermarket1_lng = nearest_supermarket[0]['longitude'],
                supermarket2_lng = nearest_supermarket[1]['longitude'],
                supermarket3_lng = nearest_supermarket[2]['longitude'],
                supermarket1_lat = nearest_supermarket[0]['latitude'],
                supermarket2_lat = nearest_supermarket[1]['latitude'],
                supermarket3_lat = nearest_supermarket[2]['latitude'],
                supermarket1_name = nearest_supermarket[0]['shop_name'],
                supermarket2_name = nearest_supermarket[1]['shop_name'],
                supermarket3_name = nearest_supermarket[2]['shop_name'],
                supermarket1_phone = nearest_supermarket[0]['phone_number'],
                supermarket2_phone = nearest_supermarket[1]['phone_number'],
                supermarket3_phone = nearest_supermarket[2]['phone_number'],
                )
# Basic condition map
    return render_template(
        "POI.html",
        input_address=user_input.address,
        html_content= html_content,
        html_map_poi = html_map_poi,
        center_lng=lng,
        center_lat=lat
        )

# @app.route("/basic/", methods=["GET"])

@app.route("/transit/")
def get_transit():
    lng=user_input.lng
    lat=user_input.lat
    address=user_input.address
#Transit query
    query_bus = text("""
    SELECT "Stop_Name","Mode","Latitude","Longitude",geometry,
        ROUND(ST_Distance(geometry::geography,ST_MakePoint(:longitude,:latitude)::geography)) AS Distance
    FROM stops_philly
    WHERE "Mode"!='Highspeed'
    ORDER BY Distance
    LIMIT 5
    """)
    bus=gpd.GeoDataFrame([dict(row) for row in engine.execute(query_bus, longitude=lng, latitude=lat).fetchall()])

    query_rail = text("""
    SELECT "Stop_Name","Mode","Latitude","Longitude",geometry,
        ROUND(ST_Distance(geometry::geography,ST_MakePoint(:longitude,:latitude)::geography)) AS Distance
    FROM stops_philly
    WHERE "Mode"='Highspeed'
    ORDER BY Distance
    LIMIT 2
    """)
    rail=gpd.GeoDataFrame([dict(row) for row in engine.execute(query_rail, longitude=lng, latitude=lat).fetchall()])

    html_trans_map = render_template(
        "transportation.html",
        mapbox_token=MAPBOX_TOKEN,
        center_lng=lng,
        center_lat=lat,
        address=address,
        bus1_lng=bus['Longitude'][0],
        bus2_lng=bus['Longitude'][1],
        bus3_lng=bus['Longitude'][2],
        bus4_lng=bus['Longitude'][3],
        bus5_lng=bus['Longitude'][4],
        bus1_lat=bus['Latitude'][0],
        bus2_lat=bus['Latitude'][1],
        bus3_lat=bus['Latitude'][2],
        bus4_lat=bus['Latitude'][3],
        bus5_lat=bus['Latitude'][4],
        rail1_lng=rail['Longitude'][0],
        rail2_lng=rail['Longitude'][1],
        rail1_lat=rail['Latitude'][0],
        rail2_lat=rail['Latitude'][1],
        bus_stop1=bus['Stop_Name'][0],
        bus_stop2=bus['Stop_Name'][1],
        bus_stop3=bus['Stop_Name'][2],
        bus_stop4=bus['Stop_Name'][3],
        bus_stop5=bus['Stop_Name'][4],
        distance_bus1=bus['distance'][0],
        distance_bus2=bus['distance'][1],
        distance_bus3=bus['distance'][2],
        distance_bus4=bus['distance'][3],
        distance_bus5=bus['distance'][4],
        rail_stop1=rail['Stop_Name'][0],
        rail_stop2=rail['Stop_Name'][1],
        distance_rail1=rail['distance'][0],
        distance_rail2=rail['distance'][1]
    )

    html_trans_content = render_template(
        "trans_content.html",
        bus_stop1=bus['Stop_Name'][0],
        bus_stop2=bus['Stop_Name'][1],
        bus_stop3=bus['Stop_Name'][2],
        bus_stop4=bus['Stop_Name'][3],
        bus_stop5=bus['Stop_Name'][4],
        distance_bus1=bus['distance'][0],
        distance_bus2=bus['distance'][1],
        distance_bus3=bus['distance'][2],
        distance_bus4=bus['distance'][3],
        distance_bus5=bus['distance'][4],
        rail_stop1=rail['Stop_Name'][0],
        rail_stop2=rail['Stop_Name'][1],
        distance_rail1=rail['distance'][0],
        distance_rail2=rail['distance'][1]
    )


    return render_template(
    "TransportationPage.html",
    address=user_input.address,
    html_trans_map = html_trans_map,
    html_trans_content = html_trans_content
    )


@app.route("/shooting/")
def get_shooting():
    lng=user_input.lng
    lat=user_input.lat
    address=user_input.address
    return render_template(
    "shooting.html",
    center_lng=lng,
    center_lat=lat,
    address=address
    )

@app.route("/census_download", methods=["GET"])
def census_download():
    """Download GeoJSON of data snapshot"""
    lng = request.args["lng"]
    lat = request.args["lat"]
    data = get_geo_tract(lng, lat)
    
    return Response(data.to_json(), 200, mimetype="application/json")


# 404 page example
@app.errorhandler(404)
def page_not_found(e):
    return render_template("null_island.html", mapbox_token=MAPBOX_TOKEN), 404

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(debug=True)
