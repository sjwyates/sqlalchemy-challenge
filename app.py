import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt

## SQLAlchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station


## Flask
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    results = session.query(Station.name).all()
    session.close()

    all_stations = list(np.ravel(results))
    return jsonify(all_stations)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    results = session.query(Station.name).all()
    session.close()

    all_stations = list(np.ravel(results))
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Last date and 1 year before that
    last_date = session.query(Measurement.date)\
        .order_by(Measurement.date.desc()).first()[0]\
        .split('-')
    last_date = dt.date(*[int(str) for str in last_date])
    year_b4 = dt.date(last_date.year - 1, last_date.month, last_date.day)

    # Most active station in the last 12 months
    most_active = session.query(Measurement.station)\
        .filter(func.strftime('%Y-%m-%d', Measurement.date) >= year_b4)\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc())\
        .first()[0]

    # All the data from the last 12 months
    most_active_tobs = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active)\
        .filter(func.strftime('%Y-%m-%d', Measurement.date) >= year_b4)\
        .all()

    session.close()

    tobs = list(np.ravel(most_active_tobs))
    return jsonify({
        "id": most_active,
        "observations": tobs
    })


@app.route("/api/v1.0/ranges/")
def start_stop():
    params = request.args.to_dict()

    session = Session(engine)

    results_q = session.query(Measurement.date, Measurement.tobs)

    if params['start'] == '':
        return "No start date provided"
    else:
        start_date = dt.date(*[int(str) for str in params['start'].split('-')])
        results_q = results_q.filter(func.strftime('%Y-%m-%d', Measurement.date) >= start_date)

    if params['stop'] != '':
        stop_date = dt.date(*[int(str) for str in params['stop'].split('-')])
        results_q = results_q.filter(func.strftime('%Y-%m-%d', Measurement.date) <= stop_date)

    results = {
        "min_temp": results_q.order_by(Measurement.date).first()[0][1],
        "max_temp": results_q.order_by(Measurement.date.desc()).first()[0][1],
        "avg_temp": np.average(*[row[1] for row in results_q.all()])
    }

    session.close()

    return jsonify(results)