use mysql;
CREATE DATABASE CJ_Websim_Member;
-- CREATE DATABASE CJ_Websim_Auth;
CREATE DATABASE CJ_Websim_Log;
CREATE DATABASE CJ_Websim_Dormant;
CREATE DATABASE CJ_Websim_Withdrawal;

-- CREATE USER 'cjwebsim'@'localhost' IDENTIFIED BY 'iG!8A4#YnP';
GRANT ALL PRIVILEGES ON CJ_Websim_Member.* TO 'cjwebsim'@'localhost';
-- GRANT ALL PRIVILEGES ON CJ_Websim_Auth.* TO 'cjwebsim'@'localhost';
GRANT ALL PRIVILEGES ON CJ_Websim_Log.* TO 'cjwebsim'@'localhost';
GRANT ALL PRIVILEGES ON CJ_Websim_Dormant.* TO 'cjwebsim'@'localhost';
GRANT ALL PRIVILEGES ON CJ_Websim_Withdrawal.* TO 'cjwebsim'@'localhost';

use CJ_Websim_Member;
CREATE TABLE Users (
    user_no INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(20),
    login_type VARCHAR(20) -- "SSO" / "EXCEPT"
);
CREATE TABLE Profile (
    profile_id INT AUTO_INCREMENT PRIMARY KEY,
    user_no INT,
    cell_phone VARCHAR(128), -- base64 encryt
    email VARCHAR(128), -- base64 encryt
    cj_world_account VARCHAR(30), -- base64 encryt
    join_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    authentication_level VARCHAR(20) NOT NULL, -- 'User'/'Admin'
    FOREIGN KEY(user_no) REFERENCES CJ_Websim_Member.Users(user_no)
);

use CJ_Websim_Auth;
CREATE TABLE Password (
    password_id INT AUTO_INCREMENT PRIMARY KEY,
    user_no INT,
    salt VARCHAR(128),
    update_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    password VARCHAR(128),
    FOREIGN KEY(user_no) REFERENCES CJ_Websim_Member.Users(user_no)
);

use CJ_Websim_Log;
CREATE TABLE User_activity_log (
    user_activity_log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_no INT,
    menu_name VARCHAR(30),
    calculation_log VARCHAR(256), -- 
    log_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_no) REFERENCES CJ_Websim_Member.Users(user_no)
);
CREATE TABLE Db_activity_log (
    db_activity_log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_no INT,
    table_name VARCHAR(30),
    row_id INT, 
    activity_code CHAR(1), -- C:Create,R:Read,U:Update,D:Delete
    as_is VARCHAR(256),
    to_be VARCHAR(256),
    modifier TINYINT DEFAULT 1, -- 1:user,2:admin,3:etc
    log_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_no) REFERENCES CJ_Websim_Member.Users(user_no)
);
CREATE TABLE Withdrawal_log (
    withdrawal_log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_no INT,
    withdrawl_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_no) REFERENCES CJ_Websim_Member.Users(user_no) 
);
CREATE TABLE Login_log (
    login_log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_no INT,
    status_code TINYINT, -- 0: Fail, 1: Success
    ip VARCHAR(15),
    -- fail_count TINYINT,
    -- fail_reason TINYINT,
    login_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_no) REFERENCES CJ_Websim_Member.Users(user_no) 
);