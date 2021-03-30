import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup

engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# Reflect an existing database into a new model

Base = automap_base()

# Reflect the tables

Base.prepare(engine, reflect=True)

# Save reference to the tables.
Measurement = Base.classes.measurement
Station = Base.classes.station

# print(Base.classes.keys())

 # Create our session (link) from Python to the DB.
session = Session(engine)

# Flask Setup

app = Flask(__name__)

# Flask Routes

# Set the home page and list all routes that are available


@app.route("/")
def home():
    return ("List all available api routes:<br/>"
        "/api/v1.0/precipitation <br/>"
        "/api/v1.0/stations <br/>"
        "/api/v1.0/tobs <br/>"
        "/api/v1.0/<start> <br/>"
        "/api/v1.0/<start>/<end> <br/>"
    )

#Convert the query results to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date 1 year ago from the last data point in the database.
    date_one_yr_ago_dt = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores.
    
    last_year = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date >= date_one_yr_ago_dt).all()

    # Convert the query results to a dictionary using date as the key and prcp as the value.

    all_precipication = []
    for date, prcp in last_year:
            precip_dict = {}
            precip_dict[date] = prcp
            all_precipication.append(precip_dict)

    return jsonify(all_precipication)

#Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
   
    # Query for stations.
    number_stations = session.query(Station.station).all()

    # Convert the query results to a dictionary.

    all_stations = list(np.ravel(number_stations))

    return jsonify(all_stations)

#Query the dates and temperature observations of the most active station for the last year of data.

#Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    

    # Calculate the date 1 year ago from the last data point in the database.

    date_one_yr_ago_dt = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Perform a query to retrieve the date and temperature scores for the most active station from the last year.

    #SELECT tobs FROM Measurement WHERE station = "USC00519281" AND date >= date_one_yr_ago_dt

    temp_recordings = session.query(Measurement.tobs).\
    filter(Measurement.station == "USC00519281").filter(Measurement.date >= date_one_yr_ago_dt).all()

    # Convert the query results to a dictionary using date as the key and temperature as the value.

    all_temperatures = list(np.ravel(temp_recordings))

    return jsonify(all_temperatures)

#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route('/api/v1.0/<start>', defaults={'end': None})
@app.route("/api/v1.0/<start>/<end>")
def date_range(start=None, end=None):

    if not end:
        temp_stats = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.station == "USC00519281").all()

        temp_list = list(np.ravel(temp_stats))

        return jsonify(temp_list)

    temp_stats = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.station == "USC00519281").all()

    temp_list = list(np.ravel(temp_stats))

    return jsonify(temp_list)


if __name__ == '__main__':
    app.run(debug=True)