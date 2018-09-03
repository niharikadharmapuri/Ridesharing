from urllib.request import urlopen
import json
import networkx as nx
import dbconnect
from datetime import timedelta
import timeit
import argparse
import details

input_for_max_match = nx.Graph()
total_trips = 0
total_lone_trips = 0
total_saved_trips = 0
total_trip_distance = 0
total_saved_distance = 0
total_running_time = 0
total_distancegain = 0
total_ss = 0
count = 0
merged_trips = []



def merge_trips(passenger_constraint,trips,walk):# list of trip instances in a pool
    global total_saved_trips
    global total_lone_trips
    global total_trips
    global total_trip_distance
    global total_saved_distance
    global total_running_time
    global count
    global merged_trips
    global total_distancegain
    
    input_for_max_match.clear()# clear the list
    no_of_trips = 0
    trip_distance = 0

    if trips is not None:
        no_of_trips += len(trips)# in a pool

    for trip in trips:
        trip_distance += trip.trip_distance# sum all tripdist in a pool

    # initialize the trip processing matrix to -1 to denote that the trips are yet to be processed
    # Merged trip pairs are set to 1 to avoid re-processing.
    start = timeit.default_timer()
    trips_processed = [[-1 for x in range(no_of_trips)] for y in range(no_of_trips)]
    i = 0
    while i < len(trips):
        j = i + 1
        trip_1 = trips[i]
        while j < len(trips):
            trip_2 = trips[j]
            #Processing un-processed trips alone!
            if (trip_1.trip_id != trip_2.trip_id) and (trips_processed[i][j] == -1):# trips not same items and not processed yet
                passenger_count = trip_1.passenger_count + trip_2.passenger_count# if constaint satisfied
                if passenger_count <= passenger_constraint and are_trips_mergeable(trip_1, trip_2, walk):# check passenger constraint
                    trips_processed[i][j] = 1 # merge them
                    trips_processed[j][i] = 1
                else:
                    trips_processed[i][j] = 0 # lone trips. maxtrix changed to 0
                    trips_processed[j][i] = 0
            else:# either same items and  already processed 
                trips_processed[i][j] = 0
                trips_processed[j][i] = 0
            j = j + 1
        i = i + 1
    matched = max_matching(input_for_max_match)# input is shareability network and output is subset of edges that are merged actually
    stop = timeit.default_timer()
    running_time = stop - start
    total_running_time += running_time# for all pools in the time chunk
    pool_savings = 0
    distancegain = 0
    for trip1,trip2 in matched: # in finally merged trips. for a given pool
        distancegain = input_for_max_match[trip1][trip2]["distance"] #                    distance gained due to ridesahring is the value on edge
        od = trip1.trip_distance + trip2.trip_distance #  total distance if they go alone     HA+HB                  
        td = distancegain * od ##                        HA+AB             total dist if they ride share
        sd = od - td ## saved distance
        pool_savings += sd
        merged_trips.append((trip1.trip_id,trip2.trip_id))# add merged trips tuples to the list

    lone_trips = no_of_trips - (len(matched) * 2)
    saved_trips = len(matched)
    total_trips += no_of_trips
    total_saved_trips += saved_trips
    total_lone_trips += lone_trips
    total_trip_distance += trip_distance
    total_saved_distance += pool_savings
    total_distancegain += distancegain
    count += 1 # counts the number of pools made in the time chunk



# Function to perform the max_matching algorithm by calling the networkx api
def max_matching(input_for_max_match):
    matched = nx.max_weight_matching(input_for_max_match, maxcardinality=True)
    return matched

def are_trips_mergeable(trip_1, trip_2,walk):
    if (trip_1.willing_to_walk or trip_2.willing_to_walk) and walk:
        return are_trips_mergeable_walk(trip_1,trip_2) # with walking
    else:
        return are_trips_mergeable_no_walk(trip_1, trip_2) # without walking


def are_trips_mergeable_walk(trip_1,trip_2):
    if trip_1.trip_duration <= trip_2.trip_duration and trip_1.willing_to_walk and len(trip_1.ballparks)>0:#if 1 is near and he is willing to walk
        new_dropoff_lat, new_dropoff_lon = find_best_dropoff(trip_1,trip_2)# drop off for trip1
        trip_1.dropoff_latitude = new_dropoff_lat# change the drop off location for the trip1
        trip_1.dropoff_longitude = new_dropoff_lon

    if trip_2.trip_duration < trip_1.trip_duration and trip_2.willing_to_walk and len(trip_2.ballparks)>0:
        new_dropoff_lat, new_dropoff_lon = find_best_dropoff(trip_2, trip_1)# drop off for trip2
        trip_2.dropoff_latitude = new_dropoff_lat
        trip_2.dropoff_longitude = new_dropoff_lon

    return are_trips_mergeable_no_walk(trip_1,trip_2)

def are_trips_mergeable_no_walk(trip_1, trip_2):# yes if delay consraint is satisfied
    # A B
    url = "http://router.project-osrm.org/route/v1/driving/" + str(trip_1.dropoff_longitude) + "," + str(trip_1.dropoff_latitude) + ";" + str(trip_2.dropoff_longitude) + "," + str(trip_2.dropoff_latitude)
    try:
        response = urlopen(url)
        string = response.read().decode('utf-8')
        json_obj = json.loads(string)
        if json_obj is not None:
            duration_between_two_trips = json_obj['routes'][0]['duration']
            distance_between_two_trips = json_obj['routes'][0]['distance'] * float(0.000621371)
            if trip_1.trip_duration <= trip_2.trip_duration:# nearest destination is the edge one
                edge_one = trip_1.trip_duration
                edge_two = trip_2.trip_duration
                delay_threshold = trip_2.delay_threshold
                distance_one = trip_1.trip_distance
                distance_two = trip_2.trip_distance
            else:
                edge_one = trip_2.trip_duration
                edge_two = trip_1.trip_duration
                delay_threshold = trip_1.delay_threshold
                distance_one = trip_2.trip_distance
                distance_two = trip_1.trip_distance
            result = check(edge_one, edge_two, duration_between_two_trips,delay_threshold)# to check delay constraint
            if result:
                distance_gain = calculate_distance_gain(distance_one,distance_two,distance_between_two_trips)
                sharing_gain = distance_gain # ratio
                input_for_max_match.add_nodes_from([trip_1,trip_2])# constructing shareability network
                input_for_max_match.add_edge(trip_1,trip_2,weight=sharing_gain,distance=distance_gain)
            return result
        else:
            return False
    except:
        return False


def find_best_dropoff(t1,t2):# find dropoff for t1 from the ballparks so that dist ball park to B is minimized
    url = "http://router.project-osrm.org/route/v1/driving/" + str(t1.dropoff_longitude) + "," + str(t1.dropoff_latitude) + ";" + str(t2.dropoff_longitude) + "," + str(t2.dropoff_latitude)
    #cal dist between A and B
    try:
        response = urlopen(url)
        string = response.read().decode('utf-8')
        json_obj = json.loads(string)
        if json_obj is not None:
            min = json_obj['routes'][0]['distance'] * float(0.000621371)# cal dist between A and B
            best_lat = t1.dropoff_latitude
            best_lon = t1.dropoff_longitude
        for l1,l2 in t1.ballparks: # try each ballpark and find dist between ballpark1 and B
            url = "http://router.project-osrm.org/route/v1/driving/" + l2 + "," + l1 + ";" + str(t2.dropoff_longitude) + "," + str(t2.dropoff_latitude)
            try:
                response = urlopen(url)
                string = response.read().decode('utf-8')
                json_obj = json.loads(string)
                if json_obj is not None:
                    dist = json_obj['routes'][0]['distance'] * float(0.000621371)
                    if dist < min:
                        best_lat = l1
                        best_lon = l2
            except:
                continue
        return best_lat ,best_lon
    except:
        return 0,0


def calculate_distance_gain(d1,d2,distance_between): # ratio of with RS/without RS
    return float((d1 + distance_between) / (d1 + d2))



def processballparks(points):
    ballparks = []# list of ballpark tuples
    if points != '0' and len(points) > 1:
        points = points.split('|')
        for p in points:
            x,y = p.split('#')
            ballparks.append((x,y))
    return ballparks


def check(d1, d2, duration_between, delay_threshold):# 0.3
    increased_duration = ((d1 + duration_between) - d2) / d2
    if increased_duration <= delay_threshold:
        return True
    else:
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p",default=3,type=int,choices=[3,5,7],help="Pool window in minutes")
    parser.add_argument("-walk",default=1,type=int,choices=[0,1],help="Include walking?")
    parser.add_argument("-w",default=5,type=int,choices=[0,1,2,3,4,5],help="Run for how many weeks?")
    parser.add_argument("-d",default=10,type=int,choices=range(1,32),help="Enter day for January!")
    parser.add_argument("-hr",default=8,type=int,choices=range(0,24),help="Enter begin hour")
    parser.add_argument("-hd", default=1, type=int, choices=range(1,24), help="Enter hour delta")
    #parser.add_argument("-o",required=True,help="Output File")
    args = parser.parse_args()
    poolwindow = args.p
    walk = args.walk
    weeks = args.w
    #outfile = args.o
    outfile='output.csv'
    connection_object = dbconnect.open_db_connection()
    cursor = connection_object.cursor()
    if weeks > 0:
        q = "select * from RideSharingTrips.trip_details where pickup_datetime order by pickup_datetime"# increasing order of time
    else:
        day = args.d
        hour = args.hr # begin hour
        hd = args.hd # hour delta
        if hour < 10:
            beginhour = str(0) + str(hour)# 09
        else:
            beginhour = str(hour)
        begindate = '2016-01-' + str(day) + ' ' + beginhour + ':00:00'
        q = "select * from RideSharingTrips.trip_details where pickup_datetime >= ('%s') order by pickup_datetime" % (begindate)

    cursor.execute(q)
    first_record = cursor.fetchone()
    if weeks > 0:
        startdate = first_record[1]  # pickup_datetime
        enddate = first_record[1] + timedelta(minutes=poolwindow)  # pool window - 3 minute
        stopdate = startdate + timedelta(weeks=weeks)
    else:
        startdate = first_record[1]  # pickup_datetime
        enddate = startdate + timedelta(minutes=poolwindow)  # pool window - 3 minute# each pool window
        stopdate = startdate + timedelta(hours=hd)#  whole of the time chunk

    while (enddate <= stopdate):# loop through all of the windows in the time chunk 
        query = "select * from RideSharingTrips.trip_details where pickup_datetime between ('%s') and ('%s')" % (startdate, enddate)
        cursor.execute(query)
        if cursor == None:
            break
        else:
            trips = []# stores the trip instances in a pool in the list
            for record in cursor: # for each trip in the pool
            # sql table
            #trip_id 0, pickup_datetime 1, passenger_count 2, dropoff_longitude 3, dropoff_latitude 4,
            #trip_duration 5, trip_distance 6, delay_threshold 7, willing_to_walk 8, walking_threshold 9, ballparks 10) 11columns
            #
            #datawithballparks.csv
            # Trip_id 0, tpep_pickup_datetime 1, tpep_dropoff_datetime 2, passenger_count 3,  sourcelongitude 4, sourcelatitude 5, destinationlongitude 6,
            #destinationlatitude 7,  trip_distance(original) 8, trip_distance(osrm) 9 , trip_duration(osrm)10 , delaythreshold 11, willing_to_walk 12, walkingthreshold 13,
            # ballparks 14  15columns


                trip = details.TripDetails(record[0], record[1], record[3], record[6], record[7], record[10],
                                                       record[9], record[11],record[12],record[13],processballparks(record[14]))
                trips.append(trip)
            merge_trips(3,trips,walk)# call merge_trips on each pool 

            #poll database here, per pool window
            startdate = enddate + timedelta(seconds=1)# consider times by incrementing one second
            enddate = startdate + timedelta(minutes=poolwindow)# pool size

    avg_trips = int(total_trips/count)
    avg_lone_trips = int(total_lone_trips/count)
    avg_saved_trips = int(total_saved_trips/count)
    avg_original_distance = total_trip_distance/count
    avg_saved_distance = total_saved_distance/count
    avg_running_time = total_running_time/count
    avg_dg = total_dg/count

    with open(outfile,'w') as f:
        if weeks > 0:
            print("****** Pool window - {} minute - Statistics, Time Period - {} week ******".format(poolwindow,weeks),file = f)
        else:
            print("****** Pool window - {} minute - Statistics, Time Period - 01/{}/2016, Hours Between {}:00:00 and {}:00:00 ******".format(poolwindow, day, hour, hour + hd), file=f)

        print("Merged Trips - {}".format(merged_trips),file = f)
        print("Total Trips - {}".format(total_trips),file = f)
        print("Total Lone Trips - {}".format(total_lone_trips),file = f)
        print("Total Saved Trips - {}".format(total_saved_trips),file = f)
        print("Total Original Distance - {} miles".format(total_trip_distance),file = f)
        print("Total Distance Saved - {} miles".format(total_saved_distance),file = f)
        print("Total Distance Gain - {} ".format(total_dg), file=f)
        print("Percentage Savings - {}%".format(round((total_saved_distance / total_trip_distance) * 100), 0), file=f)
        print("Total run time to compute matches - {} minutes".format(total_running_time / 60), file=f)
        print("***************************************************************************", file=f)
        print("Average Trips - {}".format(avg_trips), file = f)
        print("Average Lone Trips- {}".format(avg_lone_trips),file = f)
        print("Average Saved Trips - {}".format(avg_saved_trips), file = f)
        print("Average Original Distance in a pool window - {} miles".format(avg_original_distance), file = f)
        print("Average Distance Saved - {} miles".format(avg_saved_distance), file = f)
        print("Average Distance Gain - {}".format(avg_dg), file=f)
        print("Average Running Time - {} seconds".format(avg_running_time), file = f)
        print("***************************************************************************", file = f)
    f.close()

if __name__ == "__main__":
    main()
