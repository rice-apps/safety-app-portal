# app.py
# (c) Rice Apps 2017

import os
import config
from flask import Flask, request, g, render_template, jsonify
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

# Flask
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Services
socketio = SocketIO(app)
db = SQLAlchemy(app)

# DB Tables
from models import BlueButtonRequest as Req
from models import Number
from models import Case


#########################################################################################
# Routing
#########################################################################################


@app.route('/')
def webEndpoint():
    return render_template('index.html')


@app.route("/api/numbers", methods=['GET'])
def numbersEndpoint():
	numbers = Number.query.order_by(Number.name).all()
	return jsonify({"result": [i.serialize for i in numbers]})


@app.route("/api/bb_request", methods=['POST', 'GET', 'DELETE'])
def locationEndpoint():
	# Get the location in the database
    if request.method == 'GET':
        return location_get()

    # Add location into the database
    if request.method == 'POST':
        return location_post()

    # Delete location according to case id
    if request.method == 'DELETE':
        return location_delete()


@app.route("/api/log", methods=['GET'])
def logEndpoint():
	requests = Req.query.order_by(Req.request_id).all()
	return get("bb-case-tracking")


@app.route("/api/resolve", methods=['POST'])
def resolveEndpoint():
	r = request.form
	case_id = r['case_id']

	return


#########################################################################################
# Messages
#########################################################################################


@socketio.on('connect')
def clientConnect():
	print "SocketIO client connected."


#########################################################################################
# Helpers
#########################################################################################


def get(tableName):
	return


def location_get():
	""" Get only un-resolved requests """
	r = request.form

	# Case-specific get
	if 'case_id' in r:
		case_id = r['case_id']

		# Verify case id
		last_case = Case.query.order_by(desc(Case.case_id)).first()
		if case_id > last_case:
			print "Error: this case does not exist."
			return jsonify({"status":500})

		q = Req.query.join(Case, Req.case_id == Case.case_id) \
			   		 .add_columns(Req.case_id, Req.longitude, Req.latitude,
			   				Req.timestamp) \
			   		 .order_by(Req.case_id) \
			   		 .filter_by(Req.case_id == case_id and Case.resolved == False) \
			   		 .all()
		return jsonify({"result": [i.serialize() for i in q]})

	else:
		q = Req.query.join(Case, Req.case_id == Case.case_id) \
			   		 .add_columns(Req.case_id, Req.longitude, Req.latitude,
			   					  Req.timestamp) \
			   		 .order_by(Req.case_id) \
			   		 .filter_by(Req.resolved == False) \
			   		 .all()
		return jsonify({"result": [i.serialize() for i in q]})


def location_post():
	r = request.form
	case_id = r['case_id']

	# Add new case if necessary
	last_case = Case.query.order_by(desc(Case.case_id)).first()
	if last_case != case_id:
		new_id = 0 if last_case is None else last_case + 1
		try:
			c = Case(resolved=False)
			db.session.add(c)
			db.session.commit()
		except:
			print "Error: couldn't add new case."
			return jsonify({"status": 500})

	# Add to bb-case-tracking
	try: 
		req = Req(case_id=r['case_id'], 
				  device_id=r['device_id'], 
				  longitude=r['longitude'], 
				  latitude=r['latitude'], 
				  timestamp=r['timestamp'])
		db.session.add(req)
		db.session.commit()
	except:
		print "Error: couldn't add new request."
		return jsonify({"status": 500})
		
	# Send message to client
	socketio.emit('map message', f)

	return jsonify({"status": 200})


def location_delete():
	# Delete a case
	return


#########################################################################################
# Main
#########################################################################################


if __name__ == '__main__':
	socketio.run(app)

