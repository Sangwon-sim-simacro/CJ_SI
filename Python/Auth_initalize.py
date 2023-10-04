from config.Database import *
from config.Auth import *
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import requests, datetime,secrets, json
import mariadb

conn = mariadb.connect(
            user="root",
            password="root",
            host=MARIA_DB_HOST,
            port=MARIA_DB_PORT,
            database=MARIA_DB_NAME_AUTH
        )
cursor = conn.cursor()



# (#member) Users Table
create_table_query = f"""
CREATE TABLE Users (
    user_no INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(20),
    login_type VARCHAR(20)
)"""
cursor.execute(create_table_query)

# (#member) Authentication Table
create_table_query = f"""
CREATE TABLE Authentication (
    authentication_id INT AUTO_INCREMENT PRIMARY KEY,
    user_no INT,
    auth_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_no) REFERENCES Users(user_no)
)"""
cursor.execute(create_table_query)

# (#member) Profile Table
create_table_query = f"""
CREATE TABLE Authentication (
    profile_id INT AUTO_INCREMENT PRIMARY KEY,
    user_no INT,
    update_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_no) REFERENCES Users(user_no)
)"""
cursor.execute(create_table_query)

# (#Auth) Password Table
create_table_query = f"""
CREATE TABLE Password (
    password_id INT AUTO_INCREMENT PRIMARY KEY,
    user_no INT,
    salt VARCHAR(128),
    update_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    FOREIGN KEY(user_no) REFERENCES Users(user_no)
)"""
cursor.execute(create_table_query)




conn.commit()

