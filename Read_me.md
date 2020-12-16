## Livable Philly
The application aims to demographic and social-economic information, nearby amenities, transportation condition, and crime density for any place in Philadelphia.
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
<br>https://cityofphiladelphia.github.io/carto-api-explorer/#incidents_part1_part2, queried from carto.

*Public transportation stops*
<br> The data is downloaded from https://www3.septa.org/hackathon/Stops/index.php?req1=65 and stored in AWS database, queried by pgAdmin.

*Amenities*
<br> Open street map, queried by Big Query

*Basic Information*
<br>Race, age economics and housing value data come from ACS 2018 Census data. Queried by Big Query

The dataset will be hosted by Google BigQuery.
