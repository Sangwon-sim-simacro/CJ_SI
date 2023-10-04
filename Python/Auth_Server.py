from .config.Database import *
from .config.Auth import *
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import requests, datetime,secrets, json
import mariadb

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

conn = mariadb.connect(
            user=MARIA_DB_USER,
            password=MARIA_DB_PASSWORD,
            host=MARIA_DB_HOST,
            port=MARIA_DB_PORT,
            database=MARIA_DB_NAME_AUTH
        )
cursor = conn.cursor()

@app.route('/')
def board():
    return "20000 Auth_Server running"


@app.route('/token', methods=['POST'])
def token_post():
    return json.dumps()

@app.route('/event', methods=['POST'])
def event_post():
    datetime_obj = datetime.now()
    return json.dumps({"result":"event successfully insert"})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=20000)