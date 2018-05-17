# app.py
# (c) Rice Apps 2017

import os, sys, traceback, json
from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from database import db
from models import Number, Case, BlueButtonRequest as Req

# PyJWT
import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

PRIVATE_KEY = "secret_key"

# Config
# app = Flask(__name__)
class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='{%',
		block_end_string='%}',
		variable_start_string='((',
		variable_end_string='))',
		comment_start_string='{#',
		comment_end_string='#}',
    ))

app = CustomFlask(__name__)  # This replaces your existing "app = Flask(__name__)"

# for i in os.environ.keys():
# 	print i + " " + os.environ[i]

# app.config.from_object(os.environ['APP_SETTINGS'])
app.config.from_object("config.DevelopmentConfig")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Start services
socketio = SocketIO(app)
with app.app_context():
	db.init_app(app)


#########################################################################################
# Routing


# TODO: HTTP -> HTTPS?

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
	
@app.route("/api/bb_case", methods=['GET', 'POST'])
def caseEndpoint():
	"""
		End point for registering a new user

		iOS End point: {'result': case_id}

		TODO: Add 'device uuid' into the header to register
	"""

	# Provide
	if request.method == 'GET':
		# Determine Case ID to use
		last_case = Case.query.order_by(Case.case_id.desc()).first()
		case_id = 0 if last_case is None else last_case.case_id + 1
		return jsonify({"result": case_id})
	elif request.method == 'POST':
		jwt_token = case_create()
		return jsonify({"token": jwt_token})
	else:
		# Unsupported method
		return jsonify({"status": 400})
	
	
@app.route("/api/bb_log", methods=['GET'])
def logEndpoint():
	requests = Req.query.order_by(Req.request_id).all()
	return jsonify({"result": [i.serialize() for i in requests]})
	
@app.route("/api/bb_resolve", methods=['POST'])
def resolveEndpoint():
	r = request.form
	case_id = r['case_id']
	
	case_resolve(case_id)
	
	return


#########################################################################################
# Messages

@socketio.on('connect')
def clientConnect():
	print "SocketIO client connected."
	connect_msg = {"status": "success"}
	socketio.emit('connect confirm', connect_msg)
	print "Finish emit"
	

#########################################################################################
# Helpers

## TODO: Param -> request.form

def date_handler(obj):
	if hasattr(obj, 'isoformat'):
		return obj.isoformat()

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
			return jsonify({"status": 500})
		
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
			.filter_by(resolved=0) \
			.all()
		
		data = []
		for item in q:
			d = item._asdict()
			data.append(d)
		
		res = {"result": data}
		
		return json.dumps(res, default=date_handler)


def location_post():
	"""
		Content-Type: application/json

	"""
	print "[Reuqest] " + str(request)
	print "[Form] " + str(request.form)
	print "[JSON DATA] " + str(request.get_json())

	r = request.get_json()

	# Verify required field
	# TODO: is checing 'case_id' necessary?
	#		if new case, is 'case_id' in the request headers?
	try:
		case_id = r['case_id']
		device_id = r['device_id']
		longitude = r['longitude']
		latitude = r['latitude']

	except KeyError as e:
		print sys.exc_info()
		return jsonify({"status": 400})
	
	# Add new case if necessary
	last_case = Case.query.order_by(Case.case_id.desc()).first()
	if last_case :
		c = Case(resolved=0)
		try:
			db.session.add(c)
			db.session.commit()
			case_id = c.case_id
			print "[New Case] " + str(c.serialize())
		except:
			print "Error: couldn't add new case: ", sys.exc_info()[1]
			return jsonify({"status": 500})

	# Add to bb-case-tracking
	try:
		req = Req(case_id=case_id,
		          device_id=device_id,
		          longitude=longitude,
		          latitude=latitude,
		          timestamp=db.func.current_timestamp())
		
		print "Finish generating new req."
		
		db.session.add(req)
		db.session.commit()
		
	except Exception as e:
		print e
		print "Error: couldn't add new request.", sys.exc_info()
		return jsonify({"status": 500})

	
	# Send useful information to the front end
	map_msg = {"case_id": r['case_id'],
	           "latitude": r['latitude'],
	           "longitude": r['longitude']}
	
	# Send message to client
	socketio.emit('map message', map_msg)
	
	return jsonify({"status": 200})
	
def location_delete():
	# Delete a case
	
	
	
	return
	

def case_resolve(case_id):
	"""
	
	:param case_id:
	:type case_id: int
	:return: null
	"""
	
	Req.query.join(Case, Req.case_id == case_id).update().values(resolved='1')
	return

def case_create():
	"""
		Create a new case and returns the encrypted token to the user
		if user didn't pass the uuid, assume it is a new user

	"""
	r = request.get_json()
	uuid = r['uuid']
	

	try:
		token = r['token']
	except KeyError:
		print "Error: Failed to load token from POST request"

		"""
			TODO: Check with db to see whether this uuid has been registered
		"""

		# Generate a new token given uuid
		token = validate_user(uuid)
	
	validate_token(token, uuid)

	return token

		


#########################################################################################
# Main

def insert_number():
	data = []
	numbers = json.load(open('data/numbers_data.json'))['data']
	try:
		for n in numbers:
			row = Number(name=n['name'], number=n['number'], on_campus=n['onCampus'], all_day=n['allDay'],
			             description=n['description'])
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

def validate_user(user_id):
	"""
		
	"""
	data = {"user_id": user_id}
	
	# Open the private key
	with open("key/publickey.pem", "rb") as key_file:
		private_key = serialization.load_pem_private_key(
			key_file.read(),
			password=None,
			backend=default_backend()
		)
	
	# Encode the data with private key
	# The token that will be given to the client
	jwt_token = jwt.encode(data, key=private_key, algorithm='RS256')

	return jwt_token

def validate_token(token, user_id):
	# Open the private key
	with open("key/publickey.pem", "rb") as key_file:
		private_key = serialization.load_pem_private_key(
			key_file.read(),
			password=None,
			backend=default_backend()
		)
	
	try:
		data = jwt.decode(token, private_key.public_key())
		if (data["user_id"] == user_id):
			return True
		else:
			return False
	except jwt.exception.DecodeError as e:
		print("Failed to validate the token")
		return False
	


if __name__ == '__main__':
	socketio.run(app)
	if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
		if len(sys.argv) > 1:
			if sys.argv[1] == '-r':
				populate_db()
