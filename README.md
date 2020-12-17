## Livable Philly
<br>[Launch the app](http://tolivablephilly-env.eba-wa279umj.us-east-1.elasticbeanstalk.com/)
The application aims to provide demographic and social-economic information, nearby amenities, transportation condition, and crime density for any place in Philadelphia to users.
<br>[Proposal](https://github.com/MUSA-509/final-project-jacey-tingting/blob/main/FinalProjectProposal.md)
![webarc](https://github.com/MUSA-509/final-project-jacey-tingting/blob/main/Web_Architecture.png)
There are four web pages in the app.
### Homepage
![indexpage](https://github.com/MUSA-509/final-project-jacey-tingting/blob/main/Index_preview.png)
### Basic Info & Amenity
![basicpage](https://github.com/MUSA-509/final-project-jacey-tingting/blob/main/Amenity_preview.png)
### Transportation
![transpage](https://github.com/MUSA-509/final-project-jacey-tingting/blob/main/transportation_preview.png)
### Crime
![crimepage](https://github.com/MUSA-509/final-project-jacey-tingting/blob/main/crime.png)

## Data

*Crime data*
<br>shooting victim data: https://phl.carto.com/api/v2/sql?q=SELECT+*+FROM+shootings&filename=shootings&format=geojson&skipfields=cartodb_id, queried from carto.

*Public transportation stops*
<br> SEPTA stop and station location: https://services2.arcgis.com/9U43PSoL47wawX5S/arcgis/rest/services/Spring_2019_Stops_By_Route/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json , the data is stored in AWS database, queried by pgAdmin.

*Amenities*
<br> Open street map, queried by Big Query

*Basic Information*
<br>Race, age economics and housing value data come from ACS 2018 Census data. Queried by Big Query.
