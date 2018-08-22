# RideSharing Project
The objective of this project is to develop ride sharing mechanism, where in the distance saved due to ride sharing is maximized thereby saving money and  reducing the carbon footprint. To do so an algorithm was developed to maximize the distance saved in such a way that user experience is maximized(quick turn around time)


2016 Yellow cabs data was mined to develop the algorithm. The goal was to identify which pool window size, delay constraint would give the best results

The project has following files:
1. tripdetails.sql  it contains table creation statement to store the trips
2. tripdetails.py it contains the trip details class, which will be used to populate the SQL table
3. cleanup.py file to clean the input csv file
4. preprocessing.py file to add trip distance, duration obtained from OSRM, and other parameters
5. ballparks.py file adds ballparks as a column to the data 
6. dbconnect.py is used to connect to db(usin sql)
7. algorithm.py contains the actual algorithm

The passenger count denotes count without driver. We are considering max capacity of car without driver to be 3. So at max 3 passengers can fit. To rideshare, we need to look for trips with less than 3 passnegers ie, passnegers count should not be more than 2

## Installation:
You require python to be installed for running the project which can be found at <br/>
		https://www.python.org/downloads/

You need to install dependent packages from requirements.txt using <br/>
		pip install -r requirements.txt

## Running the project:
The 2016 Yellow cabs data  can be found at <br/>
http://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml.

After downloading the file.Run cleanup.py file to generate cleanedupfile.csv. 
Use this as input and run preprocessing.py to obtain the preprocessedfile.csv file.
Use this file to run  ballparks.py to run obtain the datawithballparks.csv file. This is the file that would be used by the algorithm
