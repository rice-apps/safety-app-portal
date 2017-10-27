# app.py
# (c) Rice Apps 2017

import os, sys, traceback, json
from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from database import db
from models import Number, Case, BlueButtonRequest as Req

# Config
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Start services
socketio = SocketIO(app)
with app.app_context():
	db.init_app(app)

#########################################################################################
# Routing

@app.route('/')
def webEndpoint():
	""" Get index """
	return render_template('index.html')

@app.route("/api/numbers", methods=['GET'])
def numbersEndpoint():
	""" Get numbers """
	numbers = Number.query.order_by(Number.name).all()
	return jsonify({"result": [i.serialize() for i in numbers]})

@app.route("/api/bb_request", methods=['POST', 'GET', 'DELETE'])
def requestEndpoint():
	""" Blue button request endpoint """

	# Get the location in the database
	if request.method == 'GET':
		return location_get()

	# Add location into the database
	if request.method == 'POST':
		return location_post()

	# Delete location according to case id
	if request.method == 'DELETE':
		return location_delete()

@app.route("/api/bb_case", methods=['GET'])
def caseEndpoint():
	last_case = Case.query.order_by(Case.case_id.desc()).first()
	case_id = 0 if last_case is None else last_case.case_id + 1
	print case_id
	return jsonify({"result": case_id})

@app.route("/api/bb_log", methods=['GET'])
def logEndpoint():
	requests = Req.query.order_by(Req.request_id).all()
	return jsonify({"result": [i.serialize() for i in requests]})

@app.route("/api/bb_resolve", methods=['POST'])
def resolveEndpoint():
	r = request.form
	case_id = r['case_id']

	return

#########################################################################################
# Messages

@socketio.on('connect')
def clientConnect():
	print "SocketIO client connected."

#########################################################################################
# Helpers

def location_get():
	""" Get only un-resolved requests """
	r = request.form

	# Case-specific get
	if 'case_id' in r:
		case_id = r['case_id']

		# Verify case id
		last_case = Case.query.order_by(Case.case_id.desc()).first()
		if case_id > last_case.case_id:
			print "Error: this case does not exist."
			return jsonify({"status":500})

		q = Req.query.join(Case, Req.case_id == Case.case_id) \
			   		 .add_columns(Req.case_id, Req.longitude, Req.latitude,
			   				Req.timestamp) \
			   		 .order_by(Req.case_id) \
			   		 .filter_by(Req.case_id == case_id and Case.resolved == 0) \
			   		 .all()
		return jsonify({"result": [i.serialize() for i in q]})

	else:
		q = Req.query.join(Case, Req.case_id == Case.case_id) \
			   		 .add_columns(Req.case_id, Req.longitude, Req.latitude,
			   					  Req.timestamp) \
			   		 .order_by(Req.case_id) \
			   		 .filter_by(Req.resolved == 0) \
			   		 .all()
		return jsonify({"result": [i.serialize() for i in q]})

def location_post():
	r = request.form
	case_id = r['case_id']

	# Add new case if necessary
	last_case = Case.query.order_by(Case.case_id.desc()).first()
	if not last_case or last_case.case_id != case_id:
		c = Case(resolved=0)
		try:
			db.session.add(c)
			db.session.commit()
		except:
			print "Error: couldn't add new case: ", sys.exc_info()[1]
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
		print "Error: couldn't add new request.", sys.exc_info()[1]
		return jsonify({"status": 500})

	# Send message to client
	socketio.emit('map message', r)

	return jsonify({"status": 200})

def location_delete():
	# Delete a case
	return

#########################################################################################
# Main

def insert_number():
	data = []
	numbers = json.load(open('data/numbers_data.json'))['data']
	try:
		for n in numbers:
			row = Number(name=n['name'], number=n['number'], on_campus=n['onCampus'], all_day=n['allDay'], description=n['description'])
			db.session.add(row)
			db.session.commit()
	except:
		print "Error: couldn't add new number.", sys.exc_info()[1]

def reset():
	n = Number.query.delete()
	print n, " rows in Number deleted"
	b = Req.query.delete()
	print b, " rows in BB deleted"
	c = Case.query.delete()
	print c, " rows in Case deleted"

def populate_db():
	# add numbers
	with app.app_context():
		reset()
		insert_number()

if __name__ == '__main__':
	socketio.run(app)
	if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
		if len(sys.argv) > 1:
			if sys.argv[1] == '-r':
				populate_db()
	