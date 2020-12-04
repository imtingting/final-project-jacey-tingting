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

bokeh_css = CSSResources(mode="cdn", version="2.2.3", minified=True)
bokeh_js = JSResources(mode="cdn", version="2.2.3", minified=True)

app = Flask(__name__, template_folder="templates")

bqclient = bigquery.Client.from_service_account_json("Musa509-Lab5-42148b13cb70.json")

# load credentials from a file
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

# index page
@app.route("/")
def index():
    """Index page"""
    return render_template("index.html")

# Report covid tests and request time
@app.route("/amenity/", methods=["GET"])
def get_amenity():
    address = request.args.get("address")
    curr_time = datetime.now().strftime("%B %d, %Y %I:%M %p")
    if address is None:
        return f"""
        <p>No address specified, try:</p>
        <div>
        <a href="{url_for('amenity', address='Meyerson Hall, University of Pennsylvania')}">{url_for('amenity', address='Meyerson Hall, University of Pennsylvania')}</a>
        </div>
        """
    geocoding_call = (
        "https://api.mapbox.com/geocoding/v5/mapbox.places/"
        f"{address}.json?access_token={MAPBOX_TOKEN}"
    )
    resp = requests.get(geocoding_call)
    lng, lat = resp.json()["features"][0]["center"]

# Marketplace
    job_config_market = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("poi_category", "STRING", "marketplace"),
            bigquery.ScalarQueryParameter("lng", "FLOAT", lng),
            bigquery.ScalarQueryParameter("lat", "FLOAT", lat),
        ]
    )
    query_market = f"""
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

    nearest_market = [dict(row) for row in bqclient.query(query_market, job_config=job_config_market).result()]
    nearest_market1 = nearest_market[0]['amenity_name']
    nearest_market2 = nearest_market[1]['amenity_name']
    nearest_market3 = nearest_market[3]['amenity_name']
    distance_market = nearest_market[0]['distance_away_meters']

    market1_lng = nearest_market[0]['longitude']
    market2_lng = nearest_market[1]['longitude']
    market3_lng = nearest_market[2]['longitude']
    market4_lng = nearest_market[3]['longitude']
    market5_lng = nearest_market[4]['longitude']

    market1_lat = nearest_market[0]['latitude']
    market2_lat = nearest_market[1]['latitude']
    market3_lat = nearest_market[2]['latitude']
    market4_lat = nearest_market[3]['latitude']
    market5_lat = nearest_market[4]['latitude']

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
    nearest_fast_food1 = nearest_fast_food[0]['amenity_name']
    nearest_fast_food2 = nearest_fast_food[1]['amenity_name']
    nearest_fast_food3 = nearest_fast_food[3]['amenity_name']
    distance_fast_food = nearest_fast_food[0]['distance_away_meters']

    fast_food1_lng = nearest_fast_food[0]['longitude']
    fast_food2_lng = nearest_fast_food[1]['longitude']
    fast_food3_lng = nearest_fast_food[2]['longitude']
    fast_food4_lng = nearest_fast_food[3]['longitude']
    fast_food5_lng = nearest_fast_food[4]['longitude']

    fast_food1_lat = nearest_fast_food[0]['latitude']
    fast_food2_lat = nearest_fast_food[1]['latitude']
    fast_food3_lat = nearest_fast_food[2]['latitude']
    fast_food4_lat = nearest_fast_food[3]['latitude']
    fast_food5_lat = nearest_fast_food[4]['latitude']


    return render_template(
        "POI.html",
        html_content= render_template(
            "Content.html",
            address=address,
            curr_time=curr_time,
            nearest_market1=nearest_market1,
            nearest_market2=nearest_market2,
            nearest_market3=nearest_market3,
            distance_market=distance_market,
        ),
            html_map = render_template(
            "POI_map.html",
            mapbox_token=MAPBOX_TOKEN,
            center_lng= lng,
            center_lat= lat,
            market1_lng = market1_lng,
            market2_lng = market2_lng,
            market3_lng = market3_lng,
            market4_lng = market4_lng,
            market5_lng = market5_lng,
            market1_lat = market1_lat,
            market2_lat = market2_lat,
            market3_lat = market3_lat,
            market4_lat = market4_lat,
            market5_lat = market5_lat,
            fast_food1_lng = fast_food1_lng,
            fast_food2_lng = fast_food2_lng,
            fast_food3_lng = fast_food3_lng,
            fast_food4_lng = fast_food4_lng,
            fast_food5_lng = fast_food5_lng,
            fast_food1_lat = fast_food1_lat,
            fast_food2_lat = fast_food2_lat,
            fast_food3_lat = fast_food3_lat,
            fast_food4_lat = fast_food4_lat,
            fast_food5_lat = fast_food5_lat,
            )
        )


@app.route("/to_meyerson/")
def to_meyerson():
    address = request.args.get("address")
    if address is None:
        return f"""
        <p>No origin address specified, try:</p>
        <div>
        <a href="{url_for('to_meyerson', address='City Hall, Philadelphia')}">{url_for('to_meyerson', address='City Hall, Philadelphia')}</a>
        </div>
        """
    geocoding_call = (
        "https://api.mapbox.com/geocoding/v5/mapbox.places/"
        f"{address}.json?access_token={MAPBOX_TOKEN}"
    )
    resp = requests.get(geocoding_call)
    start_lng, start_lat = resp.json()["features"][0]["center"]
    end_lng=-75.1927
    end_lat=39.9522
    basemap = {"style": "mapbox://styles/mapbox/streets-v11", "token": MAPBOX_TOKEN}
    directions_resp = requests.get(
        f"https://api.mapbox.com/directions/v5/mapbox/cycling/{start_lng},{start_lat};{end_lng},{end_lat}",
        params={
            "access_token": MAPBOX_TOKEN,
            "geometries": "geojson",
            "steps": "true",
            "alternatives": "false",
        },
    )
    # list_element = '<ul>{list_items}</ul>'
    # list_items = ''.join([f"<li>{step['maneuver']['instruction']}</li>" for step in directions_resp.json()['routes'][0]['legs'][0]['steps']])
    # full_list = list_element.format(list_items=list_items)
    routes = gpd.GeoDataFrame(
         {
        "route_option": [
            str(idx) for idx in range(len(directions_resp.json()["routes"]))
        ],
        "instruction":'   '.join([step['maneuver']['instruction'] for step in directions_resp.json()['routes'][0]['legs'][0]['steps']])
         },
        geometry=[
            shape(directions_resp.json()["routes"][idx]["geometry"])
            for idx in range(len(directions_resp.json()["routes"]))
        ]
    )
    map_obj=Map(Layer(routes, color_category_style("instruction")), basemap=basemap)
    return map_obj._repr_html_()


# 404 page example
@app.errorhandler(404)
def page_not_found(e):
    return render_template("null_island.html", mapbox_token=MAPBOX_TOKEN), 404

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(debug=True)
