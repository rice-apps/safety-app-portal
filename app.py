from flask import Flask, request, g, render_template, jsonify
from flask_socketio import SocketIO
# import config

# Flask
app = Flask(__name__)
# app.config.from_object("config")

# SocketIO
socketio = SocketIO(app)


###############################################################################
# Routing
###############################################################################

@app.route('/')
def hello():
    return "Hello World!"



if __name__ == '__main__':
    app.run()

