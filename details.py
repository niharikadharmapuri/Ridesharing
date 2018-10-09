# class to store trip details

class TripDetails:
    def __init__(self, trip_id,pickup_datetime,passenger_count,dropoff_longitude,dropoff_latitude,
                 trip_duration,trip_distance,delay_threshold,willing_to_walk,walking_threshold,ballparks):
        self.trip_id = trip_id # 1
        self.pickup_datetime = pickup_datetime # 2
        self.passenger_count = passenger_count # 3
        self.dropoff_longitude = dropoff_longitude # 4
        self.dropoff_latitude = dropoff_latitude # 5
        self.trip_duration = trip_duration # 6
        self.trip_distance = trip_distance # 7 
        self.delay_threshold = delay_threshold # 8 
        self.willing_to_walk = willing_to_walk # 9 
        self.walking_threshold = walking_threshold # 10 
        self.ballparks = ballparks # 11
