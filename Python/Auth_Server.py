from config.Database import *
from config.Auth import *
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import requests, datetime,secrets, json
import mariadb

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

{
    'user_name':'sangwon',
    'pw':'sangwon',
    'login_type':'SSO',
    'cj_world_account':'sangwon_test',
    'email': 'sangwon@simacro.com',
    'cell_phone' : '010-2547-9525',
    'authentication_level' : 'admin'
}
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

    # Check duplicate
    conn_m.execute(f"SELECT * FROM users WHERE user_name = ?", (rq['user_name'],))
    isExist = conn_m.fetchone()
    if (isExist) is None:
        return "User id already exist", 409

    # CJ_Websim_Member.users insert
    insert_tuple = (rq['user_name'], rq['login_type'])
    insert_query = f"INSERT INTO users (user_name, login_type) VALUES (%s, %s)"
    conn_m.cursor().execute(insert_query, insert_tuple)
    conn_m.commit()

    # Get user_no ( Foreign key / automatically increase int value)
    conn_m.execute(f"SELECT * FROM users WHERE user_name = ?", (rq['user_name'],))
    user = conn_m.fetchone() # (user_no, user_name, login_type)
    user_no = user[0] 

    # CJ_Websim_Member.profile insert 
    insert_tuple = (user_no, rq['cell_phone'], rq['email'], rq['cj_world_account'], rq['authentication_level'])
    insert_query = f"INSERT INTO profile (user_no, cell_phone, email, cj_world_account, authentication_level) VALUES (%d, %s, %s, %s)"
    conn_m.cursor().execute(insert_query, insert_tuple)
    conn_m.commit()

    # CJ_Websim_Auth.password insert
    insert_tuple = (user_no, salt, pw)
    insert_query = f"INSERT INTO password (user_no, salt, password) VALUES (%d, %s, %s)"
    conn_a.cursor().execute(insert_query, insert_tuple)
    conn_a.commit()
        
    return "User created", 201

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