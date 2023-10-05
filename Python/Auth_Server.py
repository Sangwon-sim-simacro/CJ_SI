from config.Database import *
from config.Auth import *
from flask import make_response,Flask, jsonify, request, render_template
from flask_cors import CORS
import requests, datetime,secrets, json
import mariadb, jwt

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

conn_m = get_db_conn(MEMBER_DB)
conn_a = get_db_conn(AUTH_DB)
corsor_m = conn_m.cursor()
corsor_a = conn_a.cursor()

@app.route('/')
def board():
    return "20000 Auth_Server running"

#Token
@app.route('/token', methods=['POST'])
def create_token():
    rq = request.get_json()

    # check user exist
    corsor_m.execute(f"SELECT user_no FROM users WHERE user_name = ?", (rq['user_name'],))
    user_no = corsor_m.fetchone() # (user_no,)
    user_no = user_no[0]
    if (user_no) is None: return "User name not exist", 400

    # check authorize
    if (rq['login_type']) == 'EXCEPT':
        corsor_a.execute(f"SELECT * FROM password WHERE user_no = ?", (user_no,))
        pw_row = corsor_a.fetchone() # (password_id, user_no, salt, update_date, password)
        pw = sha256( rq['pw'] + pw_row[2] ) # check pw
        if pw == pw_row[4] : pass 
        else : return 'Id or Password is not valid', 401
    elif (rq['login_type']) == 'SSO': pass
    else: return "Bad Request", 404

    # create access token
    payload = {'exp':datetime.datetime.utcnow() + datetime.timedelta(seconds = 300), 'user_id':'test'}
    access_token = create_token_per_type(payload)

    # save refresh token to db
    refresh_token = create_token_per_type()
    insert_tuple = (user_no, refresh_token)
    insert_query = f"INSERT INTO refresh_token (user_no, refresh_token) VALUES (%s, %s)"
    corsor_a.execute(insert_query, insert_tuple)
    conn_a.commit()

    # return access token , refresh token
    return refresh_access_token_response(access_token, refresh_token)


@app.route('/token/verify', methods=['POST'])
def verify_token():
    rq = request.get_json()
    decoded_token = verify_access_token(rq['access_token'])

    if decoded_token == {} :
        return "Access Token is not valid",401
    else :
        return json.dumps(decoded_token)
    
@app.route('/token/refresh', methods=['POST'])
def refresh_token():
    rq = request.get_json()
    refresh_token = 1
    

#User
@app.route('/users', methods=['POST'])
def create_users():
    rq = request.get_json()
    salt = get_salt()
    pw = sha256( rq['pw'] + salt )

    # Check duplicate
    corsor_m.execute(f"SELECT * FROM users WHERE user_name = ?", (rq['user_name'],))
    isExist = corsor_m.fetchone()
    if (isExist) is not None: return "User id already exist", 409

    # CJ_Websim_Member.users insert
    insert_tuple = (rq['user_name'], rq['login_type'])
    insert_query = f"INSERT INTO users (user_name, login_type) VALUES (%s, %s)"
    corsor_m.execute(insert_query, insert_tuple)

    # Get user_no ( Foreign key / automatically increase int value)
    corsor_m.execute(f"SELECT * FROM users WHERE user_name = ?", (rq['user_name'],))
    user = corsor_m.fetchone() # (user_no, user_name, login_type)
    user_no = user[0] 

    # CJ_Websim_Member.profile insert 
    insert_tuple = (user_no, rq['cell_phone'], rq['email'], rq['cj_world_account'], rq['authentication_level'])
    insert_query = f"INSERT INTO profile (user_no, cell_phone, email, cj_world_account, authentication_level) VALUES (%d, %s, %s, %s, %s)"
    corsor_m.execute(insert_query, insert_tuple)
    
    # CJ_Websim_Auth.password insert
    insert_tuple = (user_no, salt, pw)
    insert_query = f"INSERT INTO password (user_no, salt, password) VALUES (%d, %s, %s)"
    corsor_a.execute(insert_query, insert_tuple)

    # commit db 
    conn_m.commit()
    conn_a.commit()
        
    return "User created", 201

@app.route('/users', methods=['DELETE'])
def delete_users():

    return json.dumps()

@app.route('/users', methods=['PUT'])
def update_users():

    return json.dumps()

@app.route('/users', methods=['PUT'])
def read_users():

    return json.dumps()



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=20000)