# app.py
# (c) Rice Apps 2017

import os
import config
from flask import Flask, request, g, render_template, jsonify
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Flask
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Services
socketio = SocketIO(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import BlueButtonCaseTracking


###############################################################################
# Routing
###############################################################################


@app.route('/')
def hello():
    return render_template('index.html')


@app.route("/api/numbers", methods=['GET'])
def numbersEndpoint():
	return


@app.route("/api/blue_button_location", methods=['POST', 'GET', 'DELETE'])
def locationEndpoint():
	# Get the location in the database
    if request.method == 'GET':
        return get_blue_button_cases()

    # Add location into the database
    if request.method == 'POST':
        return location_post("tracking_blue_button")

    # Delete location according to case id
    if request.method == 'DELETE':
        return location_delete("tracking_blue_button")


@app.route("/api/log", methods=['GET'])
def logEndpoint():
	return


###############################################################################
# Helpers
###############################################################################


def numbers_get(tableName):
	return


def location_get(tableName):
	return


def location_post(tableName):
	return


def location_delete(tableName):
	return


###############################################################################
# Main
###############################################################################


if __name__ == '__main__':
	app.run()

