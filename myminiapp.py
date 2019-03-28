from flask import Flask, render_template, request, jsonify
import json
import requests
from pprint import pprint
import requests_cache

#establishing connection with our cluster
from cassandra.cluster import Cluster
cluster = Cluster(['cassandra'], connect_timeout=30)
session = cluster.connect()

#creating my cache for the airquality site and set it to expire after 36000s, more or less 100 minutes
requests_cache.install_cache('air_api_cache', backend='sqlite', expire_after=36000)

app = Flask(__name__, instance_relative_config=True)
#creating the neccessary files to use and hide our API KEY,also defining the URL to use to fech the data
app.config.from_object('config')
app.config.from_pyfile('config.py')
air_url_template = 'https://api.breezometer.com/air-quality/v2/current-conditions?lat={latitude}&lon={longitude}&key={MY_API_KEY}&features=breezometer_aqi&metadata=True'

#defining the GET method where according to latitude and longitude provided we get response of the air quality of that specific city
@app.route('/airquality', methods=['GET'])
def airchart():
    my_latitude = request.args.get('lat','51.503399')
    my_longitude = request.args.get('lng','-0.119519')
    air_url = air_url_template.format(latitude=my_latitude, longitude=my_longitude, MY_API_KEY=app.config['MY_API_KEY']) #how the variables link with the URL
    infos = {} #creating a library to store oure results
    resp = requests.get(air_url)
    if resp.ok:
        airquality = resp.json()
        #defining the desplay and what fields from the json response will be shown in the terminal, on the left part we choose our label and on the right part the path to the information
        infos['Country'] = airquality['metadata']['location']['country']
        infos['Air Quality'] = airquality['data']['indexes']['baqi']['category']
        infos['Dominant Pollutant'] = airquality['data']['indexes']['baqi']['dominant_pollutant']
        infos['Time Stamp'] = airquality['metadata']['timestamp']

    else:
        print(resp.reason)
    return (jsonify(infos)) #showing the result on the web browser with the same format as the terminal

#defining the data set to use and the query we are perfoming
@app.route('/worldcities/<city>')
def pop(city):
    rows = session.execute("""Select * From worldcities.stats where city = '{}'""".format(city)) #this is the query performed in our data set, we are interested in the city name
#providing the results withing a formation of our liking
    for worldcities in rows:
        return('{} belongs to {} with population {} and has Lat={},Long={}'.format(worldcities.city, worldcities.country, worldcities.population, worldcities.lat, worldcities.lng))
    return('<h1> No Data found!</h1>')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
