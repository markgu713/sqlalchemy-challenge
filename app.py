# import all dependencies
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# create session
session = Session(engine)

# sort date and get the latest date
latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

# get the date for one year ago
one_year_ago = dt.datetime.strptime(latest_date, '%Y-%m-%d') - dt.timedelta(days=365)
one_year_ago

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to this weather channel!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2017-07-13<br/>"
        f"/api/v1.0/2017-07-13/2017-07-23<br/>"
        f"Note: you can change the date in the route."
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    results = (session.query(Measurement.date, func.avg(Measurement.prcp)).\
                       filter(Measurement.date >= one_year_ago).\
                       group_by(Measurement.date).all())
    return jsonify(results)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.id, Station.station, Station.name).all()
    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():
    stationsCount = (session.query(Measurement.station, func.count(Measurement.station)).\
                             group_by(Measurement.station).\
                             order_by(func.count(Measurement.station).desc()).all())
    mostActiveStation = stationsCount[0][0]
    tempQuery = (session.query(Measurement.station, Measurement.date, Measurement.tobs).\
                         filter(Measurement.station == mostActiveStation).\
                         filter(Measurement.date >= one_year_ago).all())
    return jsonify(tempQuery)

@app.route('/api/v1.0/<startDate>')
def startDateTemp(startDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results =  (session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate).\
                                    group_by(Measurement.date).all())
    temp = []                       
    for result in results:
        temp_dict = {}
        temp_dict["Date"] = result[0]
        temp_dict["Lowest Temperature"] = result[1]
        temp_dict["Average Temperature"] = result[2]
        temp_dict["Highest Temperature"] = result[3]
        temp.append(temp_dict)
    return jsonify(temp)

@app.route('/api/v1.0/<startDate>/<endDate>')
def temperature(startDate, endDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results =  (session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate).\
                                    filter(func.strftime("%Y-%m-%d", Measurement.date) <= endDate).\
                                    group_by(Measurement.date).all())
    temp = []                       
    for result in results:
        temp_dict = {}
        temp_dict["Date"] = result[0]
        temp_dict["Lowest Temperature"] = result[1]
        temp_dict["Average Temperature"] = result[2]
        temp_dict["Highest Temperature"] = result[3]
        temp.append(temp_dict)
    return jsonify(temp)

if __name__ == "__main__":
    app.run(debug=True)