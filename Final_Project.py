# MUSA 509
# HW 4
# Tingting Huang, Jacey Chang
from flask import Flask, Response, render_template, escape, request, url_for
import json
import logging
import requests
from sqlalchemy import create_engine, String, Integer
from sqlalchemy.sql import text, bindparam
from google.cloud import bigquery
import geopandas as gpd
from shapely.geometry import shape
from datetime import datetime
from cartoframes.viz import Layer, Map, color_category_style, popup_element

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
    html_response = f"""
    <div id="container" align="center" style="width:1520">

    <div id="header" align="center" style="background-color:a8dadc;">
        <h1 style="margin-bottom:0;">Let's start</h1></div>

    <div id="report" align="center" style="background-color:f1faee;height:690px;width:1520px;">
    <br>
    <img style="float: center" width="500" src="https://m1.aboluowang.com/uploadfile/2019/0818/20190818094636920.jpg" alt="welcome page">
    <br>
    <h1>Welcome!</h1>
    <h3>For covid test results at any places in Philadelphia, try "/covid_tests/?address= AN ADDRESS YOU WANT TO SEARCH"</h3>
    <h3>For route guide to Meyerson Hall, try "/to_meyerson/?address= AN ADDRESS YOU WANT TO SEARCH"</h3>
    <p>
    </p>
    </div>

    """
    response = Response(response=html_response, status=200, mimetype="text/html")
    return response

# Report covid tests and request time
@app.route("/covid_tests/")
def covid_tests():
    curr_time = datetime.now().strftime("%B %d, %Y %I:%M %p")
    address = request.args.get("address")
    if address is None:
        return f"""
        <p>No address specified, try:</p>
        <div>
        <a href="{url_for('covid_tests', address='Meyerson Hall, University of Pennsylvania')}">{url_for('covid_tests', address='Meyerson Hall, University of Pennsylvania')}</a>
        </div>
        """
    geocoding_call = (
        "https://api.mapbox.com/geocoding/v5/mapbox.places/"
        f"{address}.json?access_token={MAPBOX_TOKEN}"
    )
    resp = requests.get(geocoding_call)
    lng, lat = resp.json()["features"][0]["center"]

    query = text(
        """
    SELECT
        num_tests_positive,
        num_tests_negative,
        ST_X(ST_Centroid(geom)) as longitude,
        ST_Y(ST_Centroid(geom)) as latitude,
        zip_code
    FROM philadelphia_covid_tests
    WHERE ST_Intersects(geom, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326))
    """
    )
    resp = engine.execute(query, lng=lng, lat=lat).fetchone()
    if resp is None:
        all_zips = engine.execute(
            """
        SELECT string_agg('<a href="/covid_tests/' || zip_code || '/">' || zip_code || '</a>', ', ') as zips
        FROM philadelphia_covid_tests
        """
        ).fetchone()["zips"]
        return f"The zip code is out of Philadelphia. Try one of {all_zips}"

    nearest_hospital = get_nearest_amenity(resp["longitude"], resp["latitude"])

    html_response = f"""
    <div id="container" style="width:1520">

    <div id="header" style="background-color:a8dadc;">
        <h1 style="margin-bottom:0;">Covid Tests in Zip Code {resp['zip_code']}</h1></div>

    <div id="report" style="background-color:f1faee;height:690px;width:500px;float:left;">
        <h3>Address entered: {address}</h3>
        <h3>Request time: {curr_time}</h3>
        <p>
          In your zip code ({resp['zip_code']}) there are:
          <ul>
            <li><b style='color: green;'>{resp['num_tests_negative']} negative tests</b></li>
            <li><b style='color: red;'>{resp['num_tests_positive']} positive tests</b></li>
          </ul>
        </p>
        <p>
          Your nearest hospital is {nearest_hospital['amenity_name']}.<br />Call ahead at {nearest_hospital['phone_number']}.
        </p>
    </div>

    <div id="map" style="background-color:#EEEEEE;height:690px;width:1000px;float:left;"><img style="float: left" src="https://api.mapbox.com/styles/v1/mapbox/light-v10/static/pin-l-embassy+f74e4e({lng},{lat})/{lng},{lat},14/1020x690?access_token={MAPBOX_TOKEN}" alt="Start location"></div>

    <div id="footer" style="background-color:#FFA500;clear:both;text-align:center;"> </div>
    </div>
    """

    response = Response(response=html_response, status=200, mimetype="text/html")
    return response


def get_nearest_amenity(lng, lat, amenity_type="hospital"):
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("poi_category", "STRING", amenity_type),
            bigquery.ScalarQueryParameter("lng", "FLOAT", lng),
            bigquery.ScalarQueryParameter("lat", "FLOAT", lat),
        ]
    )
    query = f"""
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
         LIMIT 1
    """
    response = [
        dict(row) for row in bqclient.query(query, job_config=job_config).result()
    ]
    return response[0]


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
