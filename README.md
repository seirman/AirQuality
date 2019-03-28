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
We also need to create our requirements.txt file with the following content:

```
pip>=9.0.1
Flask==0.12.3
requests
requests_cache
plotly
```

We then create our Dockerfile as well with the following content:

```
FROM python:3.7-alpine
WORKDIR /myapp
COPY . /myapp
RUN pip install -U -r requirements.txt
EXPOSE 8080
CMD ["python", "myminiapp.py"]
```


To get information about AirQuality one has to write in a web browser: http://[HOSTNAME]/airquality

If we need to check another city then we need to write for example: http://[HOSTNAME]/airquality?lat=&lng= filling in lat and lng the coordinates of the city we want.

For the worldcities application we need to type: http://[HOSTNAME]/worldcities/[cityofchoice]

## Creating The Cluster in Kubernetes

Before creating our cluster we need to se the region/zone of it. It is useful to export our project name as an environment variable. We do these by the following commands:

```
gcloud config set compute/zone europe-west2-b
export PROJECT_ID="$(gcloud config get-value project -q)"
```

_The name of the zone/region may be different, I chose europe west_

First to create the Cassandra cluster we need to:

```
gcloud container clusters create cassandra --num-nodes=3
--machine-type "n1-standard-2"
```

Creating a 3 node cluster named cassandra and using machines (n1-standard-2) with two virtual CPU's and more memory than the default.
We will need three files to create our services, one as a headless service to allow peer discovery, one as Cassandra service itself and last one as replication controller for scaling up and down the number of containers. To download these files we use the following commands:

```
wget -O cassandra-peer-service.yml http://tinyurl.com/yyxnephy
wget -O cassandra-service.yml http://tinyurl.com/y6czz8e
wget -O cassandra-replication-controller.yml http://tinyurl.com/y2crfs18
```
Now we run the components:

```
kubectl create -f cassandra-peer-service.yml
kubectl create -f cassandra-service.yml
kubectl create -f cassandra-replication-controller.yml
```

Checking that our single container is running correctly and then scale up the nodes via our replication controller via these commands:

```
kubectl get pods -l name=cassandra
kubectl scale rc cassandra --replicas=3
```

## Uploading and Creating our Data Base

We get a list of our containers and pick one
```
kubectl get pods -l name=cassandra
```

And by using the name of the container we copy our data
```
kubectl cp worldcities.csv cassandra-6m799:/worldcities.csv
```
_Cassandra and database names may be different_

We run cqlsh inside the container and build our keyspace:

```
kubectl exec -it cassandra6m799 cqlsh
CREATE KEYSPACE worldcities WITH REPLICATION = {'class':'SimpleStrategy', 'replication_factor':2};
```

We further create our table and ingest the CSV via copy:

```
CREATE TABLE worldcities.stats (city text PRIMARY KEY, lat float, lng float, country text, population int);

COPY worldcities.stats(citu,lat,lng,country,population) FROM 'worldcities.csv' WITH DELIMITER=',' AND HEADER=TRUE;
```

## Connecting Flask to Cassandra and Deployment

In order to connect Flask and Cassandra we need to add inside our requirements.txt file and application code the following:

For the requirements.txt

```
pip
Flask
cassandra-driver
```

And application code

```
from flask import Flask, request
from cassandra.cluster import Cluster

cluster = Cluster(['cassandra'])
session = cluster.connect()
```

Building our image and pushing it to our Repository:

```
docker build -t gcr.io/${PROJECT_ID}.worldcities-app:v1 .
docker push gcr.io/${PROJECT_ID}/worldcities-app:v1
```
 We have exported our project id before otherwise you have to write it manually.

Now to Run it as a service we do the following:

```
kubectl run worldcities-app --image=gcr.io/${PROJECT_ID}/worldcities-app:v1 --port 8080

kubectl expose deployment worldcities-app --type=LoadBalancer --port 80 --target-port 8080
```

Finally to get the external ip for our service we use:

```
kubectl get services
```

Usually takes sometime to get the external ip. Once we have we use that followed by the name of our application. In my case was:

```
35.111.180.157/worldcities
or
35.111.180.157/airquality
```
_Since I have two different applications running in the cloud._
