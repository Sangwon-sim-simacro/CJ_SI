import base64, random, hashlib
import mariadb
from .Database import *
import datetime, jwt
from flask import make_response,Flask, jsonify, request, render_template

def get_salt () :
    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars=[]
    for i in range(16):
        chars.append(random.choice(ALPHABET))
    return "".join(chars)

def sha256 ( pw ) :
    r = hashlib.sha256( pw.encode() )
    return r.hexdigest()

def get_db_conn (db_name):
    conn = mariadb.connect(user=DB_USER,password=DB_PASSWORD,host=DB_HOST,port=DB_PORT,database=db_name)
    return conn

def create_token(token_type):
    if token_type == "access_token" :
        expire_time = 300
    elif token_type == "refresh_token" :
        expire_time = 60*60*24
    else : 
        expire_time = 300
        
    encoded = jwt.encode(
        payload = {'exp':datetime.datetime.utcnow() + datetime.timedelta(seconds = 300)},
        key = PRIVATE_KEY, 
        algorithm = 'HS256')
    token = encoded.decode('utf-8')
    return token

def verify_token( token ):
    try :
        decoded_token = jwt.decode(token, PRIVATE_KEY, algorithms=['HS256'])
        return decoded_token
    except :
        return {}
    

def refresh_access_token_response( access_token, refresh_token):
    response_data = jsonify({"access_token" : access_token})
    response = make_response(response_data)
    response.set_cookie(
        "refresh_token",value=refresh_token,max_age=24*60*60,path="/",samesite="Lax",
    )
    return response


PRIVATE_KEY = """MIIBOQIBAAJAUNfMAHNtDMS4wBuwxsVslbJuQel3OklBqICKIOvdrkzq8NBwmpZU 
Ie27KY4uCmjDouw+HRgULCOV1ok+szLjyQIDAQABAkBQwQ9lz+c5nvSR6dcu5xzt
d/xNWOIhVfYBVM0lz5Z0Of/mVbrJIXJOk95xGLx+68A16PPOmAjiKH6J6Gb5OdgB
AiEAkyJF4W6zsgxWnSuqa0I3zdAYoXLoQC4kvPYgl6DdqwECIQCMqN17DHGuUfWv
MzJd/ZSFTfWZX7pV7db9IA9dbUegyQIgdLfKgbPE3yiEiTf7gAzOoflDoMe70DYK
tM/3OPHHBwECIQCCcYPcPiEa4UUvshHummDm8vJlxyH92HC9E8NMCDEaCQIgXIDk
osXNoxRKCjx0//Gc8yMQpengBP9727068+rXF34="""