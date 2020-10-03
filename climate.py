import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
#home route

@app.route("/")
def home():
    print("Welcome to the API routes of Honolulu, HI!!")
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start-date<br/>"
        f"/api/v1.0/start-date/end-date<br/>"
    )

#precipitation route
@app.route('/api/v1.0/precipitation')
def precipication():

    #define start and end dates
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #query session to find precipitation
    precip = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    print(f'View Precipitation History from {one_year_ago} to {last_date}')

    #dictionary and jsonify
    precip_dict = dict(precip)
    return jsonify(precip_dict) 

#stations route    
@app.route('/api/v1.0/stations')
def stations():
    #query stations
    stations = session.query(Station.station).all()
    #list and jsonify
    station_names = list(np.ravel(stations))
    return jsonify(station_names)

#tobs route
@app.route('/api/v1.0/tobs')
def tobs():
    #last date    
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #query stations
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    #find most active station
    most_active_station=active_stations[0][0]
    #query tobs
    tobs = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == most_active_station).filter(Measurement.date >= one_year_ago).all()
    #dictionary and jsonify
    tobs_dict = dict(tobs)
    return jsonify(tobs_dict)

#start route
@app.route('/api/v1.0/<start>')
def only_start(start):
    canonicalized = start.replace(" ", "")
    #query min, avg, max temps
    data = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).all()
    #list and jsonify
    date_data = list(np.ravel(data))
    return jsonify(date_data)

#start and end route
@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    #define start and end date
    start_date = start.replace(" ", "")
    end_date = end.replace(" ", "")
    #query data, filter by dates
    data = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
    filter(Measurement.date >= start_date).\
    filter(Measurement.date <= end_date).all()
    #list and jsonify
    date_range_data = list(np.ravel(data))
    return jsonify(date_range_data)


if __name__ == '__main__':
    app.run(debug=True)
