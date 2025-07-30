# NFLTeamStadiums
A simple python package that provides easy access to NFL stadium data such as capacity, location, and weather.

## Installation
```
pip install nfl-stadiums
```

## Instantiation
```python
from nfl_stadiums import NFLStadiums

# Use cache if available by default
stad = NFLStadiums()

# Force new retrieval
stad = NFLStadiums(use_cache=False)

# Don't print
stad = NFLStadiums(verbose=False)
```

## Example Usage
```python
stadiums = stad.get_list_of_stadium_names()

lions_stadium_data = stad.get_stadium_by_team("lions")

stadium_data = stad.get_stadium_by_name("ford field")

coords = stad.get_stadium_coordinates_by_team("lions")

coords = stad.get_stadium_coordinates_by_name("ford field")

miles = stad.calculate_distance_between_stadiums("lions", "rams")

forecast = stad.get_weather_forecast_for_stadium('lions', '2024-05-30')

# Change parameters
forecast = stad.get_weather_forecast_for_stadium("rams", "2025/02/24", hour_start=9, hour_end=15, day_format="%Y/%m/%d")
```


### Stadium Data Example
```json
{
    "name": "Ford Field",
    "capacity": 65000,
    "imgUrl": "https://en.wikipedia.org/wiki/File:Packers_at_Lions_Dec_2020_(50715608723).jpg",
    "city": "Detroit, Michigan",
    "surface": "FieldTurf CORE",
    "roofType": "Fixed",
    "teams": [
        "Detroit Lions"
    ],
    "yearOpened": 2002,
    "sharedStadium": false,
    "currentTeams": [
        "DET"
    ],
    "coordinates": {
        "lat": 42.34,
        "lon": -83.04555556,
        "primary": "",
        "globe": "earth"
    }
}
```

### Weather Data Example
```
{
    "latitude": 42.351395, 
    "longitude": -83.06134, 
    "generationtime_ms": 0.10704994201660156, 
    "utc_offset_seconds": -14400, 
    "timezone": "America/New_York", 
    "timezone_abbreviation": "EDT", 
    "elevation": 188.0, 
    "hourly_units": 
        {
            "time": "iso8601", 
            "temperature_2m": "°F", 
            "apparent_temperature": "°F", 
            "precipitation_probability": "%", 
            "precipitation": "inch", 
            "rain": "inch", 
            "showers": "inch", 
            "snowfall": "inch", 
            "snow_depth": "ft", 
            "wind_speed_10m": "mp/h", 
            "wind_speed_80m": "mp/h", 
            "wind_direction_10m": "°"
        }, 
    "hourly": 
        {
            "time": ["2024-05-30T00:00", "2024-05-30T01:00", "2024-05-30T02:00"], 
            "temperature_2m": [50.0, 48.6, 47.3], 
            "apparent_temperature": [44.8, 43.4, 43.0], 
            "precipitation_probability": [0, 0, 0], 
            "precipitation": [0.0, 0.0, 0.0], 
            "rain": [0.0, 0.0, 0.0], 
            "showers": [0.0, 0.0, 0.0], 
            "snowfall": [0.0, 0.0, 0.0], 
            "snow_depth": [0.0, 0.0, 0.0], 
            "wind_speed_10m": [4.4, 3.5, 2.2], 
            "wind_speed_80m": [13.5, 11.1, 10.3], 
            "wind_direction_10m": [15, 18, 323]
        }
}
```

## Data and Usage
This package utilizes the Wikipedia API to retrieve NFL stadium data and Open-Meteo.com for weather information.

### You are Responsible for How You Access and Use The Data
Stadium data is fairly static, so by default, this class will save the data retrieved from Wikipedia locally for 
subsequent uses for quicker access and less load on Wikipedia. 

### Wikipedia Data
The core page is [here](https://en.wikipedia.org/wiki/List_of_current_NFL_stadiums). Wikipedia content is licensed 
under the Creative Commons Attribution-ShareAlike 3.0 Unported License. For more details on the terms of use, 
please refer to the [Wikimedia Foundation's Terms of Use](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use).

### Open Meteo
This package utilizes the Open_Meteo.com API found [here](https://open-meteo.com/). See their terms of 
use [here](https://open-meteo.com/en/terms).

## License
This project is licensed under the MIT License. See the LICENSE file for details.

