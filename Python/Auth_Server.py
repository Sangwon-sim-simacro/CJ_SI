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
conn_l = get_db_conn(LOG_DB)
corsor_m = conn_m.cursor()
corsor_a = conn_a.cursor()
corsor_l = conn_l.cursor()

@app.route('/')
def board():
    return "20000 Auth_Server running"

#Token
#Login Request == Token Create
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
        else : 
            #Login log insert (fail)
            insert_tuple = (user_no, rq['user_name'], 0, rq['ip'])
            insert_query = f"INSERT INTO login_log (user_no, user_name, status_code, ip) VALUES (%s, %s, %d, %s)"
            corsor_l.execute(insert_query, insert_tuple)
            return 'Id or Password is not valid', 401
    elif (rq['login_type']) == 'SSO': pass
    else: 
        #Login log insert (fail)
        insert_tuple = (user_no, rq['user_name'], 0, rq['ip'])
        insert_query = f"INSERT INTO login_log (user_no, user_name, status_code, ip) VALUES (%s, %s, %d, %s)"
        corsor_l.execute(insert_query, insert_tuple)
        return "Bad Request", 404
    
    # get user information for inserting accesstoken
    corsor_m.execute(f"SELECT * FROM profile WHERE user_no = ?", (user_no,))
    profile_row = corsor_m.fetchone() # (user_no, cell_phone, email, cj_world_account, join_date, update_date, authentication_level)

    # create access token
    payload = {'exp':datetime.datetime.utcnow() + datetime.timedelta(seconds = 300), 'user_no':user_no, 'cell_phone':profile_row[1],'email':profile_row[2]
               ,'cj_world_account':profile_row[3],'authentication_level':profile_row[6]}
    access_token = create_token_per_type(payload)

    # save refresh token to db
    refresh_token = create_token_per_type()
    insert_tuple = (user_no, refresh_token)
    insert_query = f"INSERT INTO refresh_token (user_no, refresh_token) VALUES (%s, %s)"
    corsor_a.execute(insert_query, insert_tuple)

    #Login log insert (success)
    insert_tuple = (user_no, rq['user_name'], 1, rq['ip'])
    insert_query = f"INSERT INTO login_log (user_no, user_name, status_code, ip) VALUES (%s, %s, %d, %s)"
    corsor_l.execute(insert_query, insert_tuple)

    #user activity log insert *(login success cases only)
    insert_tuple = (user_no, rq['user_name'], "LOGIN", "login success")
    insert_query = f"INSERT INTO user_activity_log (user_no, user_name, action_type, meta_data) VALUES (%s, %s, %s, %s)"
    corsor_l.execute(insert_query, insert_tuple)

    conn_a.commit()
    conn_l.commit()

    # return access token , refresh token
    return refresh_access_token_response(access_token, refresh_token)



@app.route('/token/refresh', methods=['POST'])
def refresh_token():
    rq = request.get_json()
    refresh_token = 1
    
#User
#------------------------------------------------------------#

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
    rq = request.get_json() # access_token / taget_user_no
    decoded_token = decode_token(rq['access_token'])
    if decoded_token == {} : return "Access Token is not valid",401
    else : pass

    # Check authentication level with access_token user_no 
    user_authentication_level = decoded_token["authentication_level"] 
    if user_authentication_level == 'admin' : pass
    else : return "Invalid request",404 

    #Delete CJ_Websim_Member.users => via ON DELTE cascade option, delete authomatically another table information
    corsor_m.execute(f"DELETE FROM users WHERE user_no = ?", (rq['taget_user_no'],))
    

    #Log insert query for Delete user history
    insert_tuple = (rq['taget_user_no'], decoded_token["user_name"] )
    insert_query = f"INSERT INTO withdrawal_log (user_no, user_name) VALUES (%s)"
    corsor_l.execute(insert_query, insert_tuple)

    # commit db
    conn_m.commit()
    conn_l.commit()

    return "Delete user", 200

@app.route('/users', methods=['PUT'])
def update_users():
    rq = request.get_json()

    decoded_token = decode_token(rq['access_token'])
    if decoded_token == {} : return "Access Token is not valid",401
    else : pass

    # Check authentication level with access_token user_no 
    # User case (need to match access_token, target_user_no)
    user_authentication_level = decoded_token["authentication_level"] 
    if user_authentication_level == 'admin' : pass
    elif user_authentication_level == 'user' and decoded_token['user_no'] == rq['target_user_no'] : pass 
    else : return "Invalid request",404 

    # update contetns confirm then write code
    update_tuple = (rq['user_name'], rq['login_type'], rq['target_user_no'])
    update_query = f"UPDATE profile set a = ?, b = ? WHERE user_no = ?"

    return json.dumps()

@app.route('/users', methods=['POST'])
def read_users():

    rq = request.get_json()

    decoded_token = decode_token(rq['access_token'])
    if decoded_token == {} : return "Access Token is not valid",401
    else : pass

    # Check authentication level with access_token user_no 
    user_authentication_level = decoded_token["authentication_level"]  
    if user_authentication_level == 'admin' : pass
    else : return "Invalid request",404 

    # join member.users, member.profile , return tuple array
    corsor_m.execute(f"SELECT * FROM users INNER JOIN profile ON users.user_no = profile.user_no")
    user_list = corsor_m.fetchall() # ( , , , )

    return json.dumps({'user_list':user_list})

#Log
#------------------------------------------------------------#
@app.route('/log', methods=['POST'])
def create_log():
    rq = request.get_json()
    decoded_token = decode_token(rq['access_token'])
    if decoded_token == {} : return "Access Token is not valid",401
    else : pass

    #user activity log insert 
    insert_tuple = (decoded_token['user_no'], decoded_token['user_name'], rq['action_type'], rq['meta_data'])
    insert_query = f"INSERT INTO user_activity_log (user_no, user_name, action_type, meta_data) VALUES (%s, %s, %s, %s)"
    corsor_l.execute(insert_query, insert_tuple)
    conn_l.commit()

    return json.dumps()

@app.route('/log', methods=['POST'])
def read_log():
    rq = request.get_json()
    decoded_token = decode_token(rq['access_token'])
    if decoded_token == {} : return "Access Token is not valid",401
    else : pass

    # rq['request_type'] : 'ENTIRE' , 'SELF'
    if rq['request_type'] == 'ENTIRE' :
        # authentical level check
        user_authentication_level = decoded_token["authentication_level"] 
        if user_authentication_level == 'admin' : pass
        else : return "Invalid request",404 

        #return entire log list
        corsor_l.execute(f"SELECT * FROM user_activity_log")
        log_list = corsor_l.fetchall() 
    elif rq['request_type'] == 'OWN' :
        user_no = decoded_token["user_no"] 
        
        #return own log list
        corsor_l.execute(f"SELECT * FROM user_activity_log where user_no = ?", (user_no))
        log_list = corsor_l.fetchall() 
    else :
        return "Invalid request",404 

    return json.dumps({"log_list":log_list})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=20000)
