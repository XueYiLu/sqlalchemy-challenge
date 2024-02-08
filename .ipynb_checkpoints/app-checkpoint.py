# Import necessary libraries
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

# Create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Define routes
@app.route("/")
def home():
    """Homepage."""
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data as a JSON dictionary."""
    # Calculate the date one year ago from the last date in the database
    one_year_ago = datetime.strptime(session.query(func.max(Measurement.date)).scalar(), '%Y-%m-%d') - timedelta(days=365)
    
    # Query precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).\
              filter(Measurement.date >= one_year_ago).all()
    
    # Convert query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations."""
    # Query all stations
    results = session.query(Station.station).all()
    
    # Convert query results to a list
    stations_list = [station for station, in results]
    
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature observations for the most active station for the previous year."""
    # Find the most active station
    most_active_station_id = session.query(Measurement.station).\
                             group_by(Measurement.station).\
                             order_by(func.count(Measurement.station).desc()).first()[0]
    
    # Calculate the date one year ago from the last date in the database
    one_year_ago = datetime.strptime(session.query(func.max(Measurement.date)).scalar(), '%Y-%m-%d') - timedelta(days=365)
    
    # Query temperature observations for the most active station for the previous year
    results = session.query(Measurement.date, Measurement.tobs).\
              filter(Measurement.station == most_active_station_id).\
              filter(Measurement.date >= one_year_ago).all()
    
    # Convert query results to a list of dictionaries
    tobs_data = [{"Date": date, "Temperature": tobs} for date, tobs in results]
    
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_stats(start=None, end=None):
    """Return JSON list of the minimum, average, and maximum temperature for a specified date range."""
    # Define query to calculate temperature statistics for a specified date range
    if end:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                  filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    else:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                  filter(Measurement.date >= start).all()
    
    # Convert query results to a list of dictionaries
    temp_stats_list = [{"Start Date": start, "End Date": end, "Min Temperature": min_temp, 
                        "Avg Temperature": avg_temp, "Max Temperature": max_temp} 
                       for min_temp, avg_temp, max_temp in results]
    
    return jsonify(temp_stats_list)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
