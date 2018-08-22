import pandas as pd
import numpy as np

# using yellow cabs 2016 january data 
df = pd.read_csv("yellow_tripdata_2016-01.csv")
# df.shape #(10,906,858, 19)
# schema:
#VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count,	trip_distance,	pickup_longitude,	pickup_latitude,	RatecodeID,	store_and_fwd_flag,	dropoff_longitude,	dropoff_latitude,	payment_type,	fare_amount,	extra,	mta_tax,	tip_amount,	tolls_amount,	improvement_surcharge,	total_amount

#passenger count is without driver
#since we are only considering merging 2 trips, max capacity of car should be 2(as there are max 3 spots in car for passengers)

df = df.drop(df[(df.passenger_count < 0) | (df.passenger_count > 2) | (df.dropoff_longitude == 0) | (df.dropoff_latitude == 0) | (df.pickup_longitude == 0) | (df.pickup_latitude == 0) | (df.RatecodeID != 2) ].index)
# df.shape #(185,034, 19)

df= df.drop(['VendorID','RatecodeID', 'store_and_fwd_flag', 'payment_type', 'extra', 'mta_tax','tip_amount','tolls_amount','improvement_surcharge','fare_amount', 'total_amount'], axis=1)

# drop unnecessary columns 
#rounding the lat long to 4 digits to make it manageable
df['pickup_latitude'] = df['pickup_latitude'].apply(lambda x: round(x,4))
df['dropoff_latitude'] = df['dropoff_latitude'].apply(lambda x: round(x,4))
df['pickup_longitude'] = df['pickup_longitude'].apply(lambda x: round(x,4))
df['dropoff_longitude'] = df['dropoff_longitude'].apply(lambda x: round(x,4))

df.index = np.arange(1, len(df) + 1)# adding index to the df # 1 to len(df)
df.to_csv("cleanedupfile.csv",index_label='Trip_Id')# 9 columns
# df.shape  (185,034, 9)
#schema of cleanedupfile is 
# Trip_id, tpep_pickup_datetime,	tpep_dropoff_datetime,	passenger_count,	trip_distance,	pickup_longitude,	pickup_latitude,	dropoff_longitude,	dropoff_latitude 