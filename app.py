import numpy as np 
import datetime as dt 

import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model 
Base = automap_base()

# Reflect the tables 
Base.prepare(engine, reflect = True)

# Save reference to the table 
Measurement = Base.classes.measurement 
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

###########################################################
# Precipitation Route 
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session (link) from Python to the DB
    session = Session(engine)

    # Query for the dates and precipitation values
    prcp_results = session.query(Measurement.date, Measurement.prcp).\
                order_by(Measurement.date).all()

    session.close()

    # Convert to list of dictionaries to jsonify
    prcp_date_list = []

    for date, prcp in prcp_results:
        new_dict = {}
        new_dict[date] = prcp
        prcp_date_list.append(new_dict)

    return jsonify(prcp_date_list)

###########################################################
# Stations route    
@app.route("/api/v1.0/stations")
def stations():
    # Create the session (link) from Python to the DB
    session = Session(engine)
    
    # Query data to get stations list
    stations = session.query(Station.station).all()

    session.close()

    # Jsonify the list 
    return jsonify(stations)

###########################################################
#  Tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Create the session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and temperature observations of the most active station for the last year of data.
    tobs_results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= '2016-08-23').\
            order_by(Measurement.date).all()

    session.close()

    # Convert list to show values 
    tobs_list = []
    for result in tobs_results:
        tlist = {}
        tlist["date"] = result[0]
        tlist["temperature"] = result[1]
        tobs_list.append(tlist)

    # Jsonify the list 
    return jsonify(tobs_list)

##########################################################
# Start route 
@app.route("/api/v1.0/<start>")
def sroute(start):

    # Create the session (link) from Python to the DB
    session = Session(engine)

    # Query minimum temperature, average temperature, and max temperature 
    start_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()

    # Jsonify the result 
    return jsonify(start_results)

##########################################################
# Start/End route
@app.route("/api/v1.0/<start>/<end>")
def stendroute(start, end):
    # Create the session (link) from Python to the DB
    session = Session(engine)

    if not end:
        stend_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()

        temps = list(np.ravel(stend_results))

        return jsonify(temps)
        

    # Query minimum temperature, average temperature, and max temperature 
    stend_results = session.query(*[func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    # Jsonify the result 
    return jsonify(stend_results)

##########################################################
#run the app
if __name__ == "__main__":
    app.run(debug=True)