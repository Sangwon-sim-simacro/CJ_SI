import base64, random, hashlib
import mariadb
from .Database import *

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

