from urllib.request import urlopen
import json
import geopy
from geopy.distance import VincentyDistance
import pandas as pd


# calculate prospective locations where the person could be droppedoff if he is willing to walk
# geopy= takes in the destination location and walking threshold, gives list of the prospective dropoff points

def calculate_ball_parks(dropoff_latitude, dropoff_longitude, walking_threshold):# returns prospective ballparks
	origin = geopy.Point(dropoff_latitude, dropoff_longitude)
	b = 0
	destinations = []
	while b < 360:# bearing
		destination = VincentyDistance(miles=walking_threshold/2).destination(origin, b)# VincentyDistance:calculate the distance between two points on the surface of a spheroid
		b = b + 45# finds 8 points in total
		lat2, lon2 = destination.latitude, destination.longitude
		destinations.append((round(lat2, 4), round(lon2, 4)))
	return destinations

# returns lat long location of the nearest points from the ball parks (actual physical location where u could drop off)
def get_nearest_point(latitude, longitude, walking_threshold):# takes in ballpark lat , ballpark long and returns points where you can actually walk to.
	url = 'http://router.project-osrm.org/nearest/v1/foot/' + str(longitude) + ',' + str(latitude) + '?number=1'
	response = json.loads(urlopen(url).read().decode('utf-8'))
	distance = response['waypoints'][0]['distance'] * 0.000621371
	if distance <= (walking_threshold/2):
		return round(response['waypoints'][0]['location'][1], 4), round(response['waypoints'][0]['location'][0], 4)
	else:
		return 0,0

# 
def all_nearest_points(dropoff_latitude, dropoff_longitude, walking_threshold):# returns a list of lat#long|lat#long|lat#long
	nearest_points = calculate_ball_parks(dropoff_latitude, dropoff_longitude, walking_threshold)# list of 8 ballparks

	new_nearest_points = []# list actual drop off for  8 ball parks 
	for each in nearest_points: #for each ballpark
		new_point = get_nearest_point(each[0],each[1], walking_threshold)# returns lat long of actual drop off 
		if new_point != (0,0):
			new_nearest_points.append(new_point)

	new_field = "|".join(str(i[0])+'#'+str(i[1]) for i in new_nearest_points)
	return new_field# lat#long|lat#long|lat#long|lat#long|lat#long|lat#long|lat#long|lat#long

# adding balparks to the csv file as  a new column
# Trip_id, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count,  sourcelongitude, sourcelatitude, destinationlongitude, destinationlatitude,
#  trip_distance(original), trip_distance(osrm), trip_duration(osrm), delaythreshold, willing_to_walk, walkingthreshold
df = pd.read_csv('preprocessedfile.csv', index_col = [0], header=None)# explicitly stating to treat the first column as the index:
new_col = []

for index, row in df.iterrows():# for each row append ballParks
	dropoff_longitude, dropoff_latitude, walking_threshold = row[6], row[7], row[13]
	if walking_threshold > 0:
		final_points = all_nearest_points(dropoff_latitude, dropoff_longitude, walking_threshold)# final points are ballparks
		new_col.append(final_points)
	else:
		new_col.append(0)

df[15] = new_col
df.to_csv('datawithballparks.csv', header=False)

## Trip_id, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count,  sourcelongitude, sourcelatitude, destinationlongitude, destinationlatitude,
#  trip_distance(original), trip_distance(osrm), trip_duration(osrm), delaythreshold, willing_to_walk, walkingthreshold

# 2	1/29/16 9:18	1/29/16 9:53	1	-73.7781	40.6413	-73.7908	40.6634	
# 15.20   	               6.801154	             31.525000	            9.4575	         1	            0.5	           40.6669#-73.7908|40.666#-73.7874|40.6635#-73.7...
