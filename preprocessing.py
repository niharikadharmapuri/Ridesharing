from urllib.request import urlopen
from random import randint
import json
import csv
import random
import requests
import time


# adding trip_distance,trip_duration obtained from OSRM.
# delaythreshold, willing_to_walk criteria ,walkingthreshold to the cleanedup data file

def preprocessing():
    sourcelatitude = "40.6413"# We are using static source
    sourcelongitude = "-73.7781"
    tripslist = []

# Trip_id, tpep_pickup_datetime,    tpep_dropoff_datetime,  passenger_count,    trip_distance,  pickup_longitude,   pickup_latitude,    dropoff_longitude,  dropoff_latitude 
    with open('cleanedupfile.csv', "rt", encoding="utf-8") as f:#
        reader = csv.reader(f)
        params = (('overview', 'false'))
        next(reader, None)
        for row in reader:
            destinationlatitude = row[8].strip()# extract the destination 
            destinationlongitude = row[7].strip()
    
            url = 'http://router.project-osrm.org/route/v1/driving/' + sourcelongitude + "," + sourcelatitude + ';'+ destinationlongitude + "," + destinationlatitude
            result = (requests.get(url)).json()
            trip_distance = result['routes'][0]['distance'] * float(0.000621371)# convert from meters to miles
            trip_duration = result['routes'][0]['duration'] / float(60)
            #print(result)
            #print('-----',result['routes'][0]['distance'],result['routes'][0]['duration'])
            time.sleep(0.2)
            willing_to_walk = randint(0, 1)# randomly assign walking criterion
            if(willing_to_walk):
                walkingthreshold = 0.5 # user is willing to walk max of these many miles
            else:
                walkingthreshold = 0
            delaythreshold = 0.3 * trip_duration# delay constraint=30% of his travel time
            tripslist.append([row[0].strip(),row[1].strip(),row[2].strip(),row[3].strip(), sourcelongitude, sourcelatitude, destinationlongitude, destinationlatitude, row[4].strip(), trip_distance,trip_duration,delaythreshold,willing_to_walk,walkingthreshold])

    with open('preprocessedfile.csv','w') as csvfile:
        csv_out = csv.writer(csvfile)
        for row in tripslist:
            csv_out.writerow(row)

preprocessing()

# cleanupfile.csv or final_input_dataTrip_Id,tpep_pickup_datetime,tpep_dropoff_datetime,passenger_count,trip_distance,pickup_longitude,pickup_latitude,dropoff_longitude,dropoff_latitude
#schema:
#Trip_id, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count,  sourcelongitude, sourcelatitude, destinationlongitude, destinationlatitude, trip_distance(original),
# trip_distance(osrm), trip_duration(osrm), delaythreshold, willing_to_walk, walkingthreshold