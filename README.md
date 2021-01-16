## Livable Philly
<br>[Launch the app](http://tolivablephilly-env.eba-wa279umj.us-east-1.elasticbeanstalk.com/)
<br>The application aims to provide demographic and social-economic information, nearby amenities, transportation condition, and crime density for any place in Philadelphia to users.
<br>[Proposal](https://github.com/MUSA-509/final-project-jacey-tingting/blob/main/FinalProjectProposal.md)
![webarc](https://github.com/MUSA-509/final-project-jacey-tingting/blob/main/Web_Architecture.png)

<br>
There are four web pages in the app.
### Homepage
![indexpage](https://github.com/imtingting/final-project-jacey-tingting/blob/main/demo/index_page.gif)
### Basic Info & Amenity
![basicpage](https://github.com/imtingting/final-project-jacey-tingting/blob/main/demo/basic_amenity.gif)
### Transportation
![transpage](https://github.com/imtingting/final-project-jacey-tingting/blob/main/demo/transportation.gif)
### Crime
![crimepage](https://github.com/imtingting/final-project-jacey-tingting/blob/main/demo/crime_density.gif)

## Data

*Crime data*
<br>shooting victim data: https://phl.carto.com/api/v2/sql?q=SELECT+*+FROM+shootings&filename=shootings&format=geojson&skipfields=cartodb_id, queried from carto.

*Public transportation stops*
<br> SEPTA stop and station location: https://services2.arcgis.com/9U43PSoL47wawX5S/arcgis/rest/services/Spring_2019_Stops_By_Route/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json , the data is stored in AWS database, queried by pgAdmin.

*Amenities*
<br> Open street map, queried by Big Query

*Basic Information*
<br>Race, age economics and housing value data come from ACS 2018 Census data. Queried by Big Query.