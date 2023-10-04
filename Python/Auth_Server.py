from .config.Database import *
from .config.Auth import *
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import requests, datetime,secrets, json
import mariadb

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/')
def board():
    return "20000 Auth_Server running"

#Token
@app.route('/token', methods=['GET'])
def read_token():
    cursor_m = get_db_conn(MEMBER_DB)
    cursor_a = get_db_conn(AUTH_DB)
    return json.dumps()

#User
@app.route('/users', methods=['POST'])
def create_users():
    rq = request.get_json()
    conn_m = get_db_conn(MEMBER_DB)
    conn_a = get_db_conn(AUTH_DB)

    salt = get_salt()
    pw = sha256( rq['pw'] + salt )

    # users insert
    insert_tuple = (rq['user_name'], rq['login_type'])
    insert_query = f"INSERT INTO users (user_name, login_type) VALUES (%s, %s)"
    conn_m.cursor().execute(insert_query, insert_tuple)
    conn_m.commit()

    if rq['login_type'] is "SSO" :
        # profile insert 
        insert_tuple = (rq['login_type'], rq['login_type'], rq['login_type'], rq['login_type'], rq['login_type'],rq['login_type'])
        insert_query = f"INSERT INTO profile (user_no, cell_phone, email, cj_world_account, join_date, authentication_level) VALUES (%d, %s, %s, %s, %d, %s)"
        conn_m.cursor().execute(insert_query, insert_tuple)
        conn_m.commit()
        # password insert
        
    elif rq['login_type'] is "EXCEPT" :
        insert_tuple = (user_id, user_name, generated_key, Now_timestamp)
        insert_query = f"INSERT INTO {table_name} (user_id, user_name, api_key, create_date) VALUES (%s, %s, %s, %d)"
        conn_m.cursor().execute(insert_query, insert_tuple)
        conn_m.commit()
    else:
        print("err")
        


    return json.dumps()

@app.route('/users', methods=['DELETE'])
def delete_users():
    cursor_m = get_db_conn(MEMBER_DB)
    cursor_a = get_db_conn(AUTH_DB)
    return json.dumps()

@app.route('/users', methods=['PUT'])
def update_users():
    cursor_m = get_db_conn(MEMBER_DB)
    cursor_a = get_db_conn(AUTH_DB)
    return json.dumps()

@app.route('/users', methods=['PUT'])
def read_users():
    cursor_m = get_db_conn(MEMBER_DB)
    cursor_a = get_db_conn(AUTH_DB)
    return json.dumps()



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=20000)