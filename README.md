# Current AirQuality and City Population REST Application

The first application returns the current air quality of the city of choice providing it's latitude and longitude with the dominant pollutant.

For the Worldcities application we assume that a Cassandra cluster is already setup.
The second application providing a city name returns the country that city belongs and also the population in 2019 that city has

## Setup

For the AirQuality application a registration for an API KEY must be made through breezometer.com
Then a folder named   instance  needs to be created, where a config.py file will be created containing our API KEY
```
DEBUG = True
MY_API_KEY = 'API KEY'
```
In the root folder create another config.py file with the following infos in:

```
DEBUG = False
```
To get information about AirQuality one has to write in a web browser: http://[HOSTNAME]/airquality

If we need to check another city then we need to write for example: http://[HOSTNAME]/airquality?lat=&lng= filling in lat and lng the coordinates of the city we want.

For the worldcities application we need to type: http://[HOSTNAME]/worldcities/[cityofchoice]
