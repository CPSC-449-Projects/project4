# Members: Quang Nguyen, Vinh Tran
# CPSC 449
# Project 4: Asynchronous Processing


import hug
import sqlite_utils
import configparser
import logging.config
import requests
import os
import socket

# Load configuration
#
config = configparser.ConfigParser()
config.read("./etc/user_services.ini")
logging.config.fileConfig(config["logging"]["config"], disable_existing_loggers=False)

@hug.startup()
def register(api):
    URL = "http://" + socket.getfqdn() + ":" + os.environ['PORT']
    payload = {'service': 'users', 'URL': URL}
    requests.post(config["registry"]["URL"]+"/register-instance/", data = payload)


# Arguments to inject into route functions
#
@hug.directive()
def sqlite(section="sqlite", key="dbfile", **kwargs):
    dbfile = config[section][key]
    return sqlite_utils.Database(dbfile)

@hug.directive()
def log(name=__name__, **kwargs):
    return logging.getLogger(name)

# Using Routes
######## Return all users in the database ########
@hug.get("/users/")
def users(db: sqlite):
    return {"users": db["users"].rows}

######## Return a specific user ########
@hug.get("/users/{username}")
def retrieve_user(response, username: hug.types.text, db: sqlite):
    users = []
    try:
        user = db["users"].get(username)
        users.append(user)
    except sqlite_utils.db.NotFoundError:
        response.status = hug.falcon.HTTP_404
    return {"users": user}

######## Return all users that the user follows ########
@hug.get("/get-following/{username}")
def get_following(username: hug.types.text, db: sqlite):
    return {"follows": db["follows"].rows_where("username = ?", [username])}

######## Create new user ########
@hug.post("/create/", status=hug.falcon.HTTP_201)
def create_user(
    response,
    username: hug.types.text,
    email_address: hug.types.text,
    password: hug.types.text,
    bio: hug.types.text,
    db: sqlite):
    users_db = db["users"]
    user = {
        "username": username,
        "email_address": email_address,
        "password": password,
        "bio": bio
    }
    try:
        users_db.insert(user)
    except Exception as e:
        response.status = hug.falcon.HTTP_409
        return {"error": str(e)}

######## Change Password ########
@hug.put("/change-password/")
def change_password(
    response,
    username: hug.types.text,
    old_password: hug.types.text,
    new_password: hug.types.text,
    db: sqlite):
    users_db = db["users"]
    try:
        user = users_db.get(username)
        if old_password == user["password"]:
            users_db.update(username, {"password": new_password})
        else:
            response.status = hug.falcon.HTTP_401
    except sqlite_utils.db.NotFoundError:
        response.status = hug.falcon.HTTP_404

######## Check password ########
@hug.get("/login/")
def login(request, response, db: sqlite):
    users_db = db["users"]
    try:
        user = users_db.get(request.params["username"])
        if request.params["password"] != user["password"]:
            response.status = hug.falcon.HTTP_401
    except sqlite_utils.db.NotFoundError:
        response.status = hug.falcon.HTTP_404

######## Follow new user ########
@hug.post("/follow/", status=hug.falcon.HTTP_201)
def add_follow(
    response,
    username: hug.types.text,
    following: hug.types.text,
    db: sqlite):
    try:
        db["follows"].insert({"username": username,"following": following})
    except Exception as e:
        response.status = hug.falcon.HTTP_409
        return {"error": str(e)}

######## Unfollow user ########
@hug.post("/unfollow/")
def unfollow(
    response,
    username: hug.types.text,
    following: hug.types.text,
    db: sqlite):
    try:
        db["follows"].delete((username, following))
    except Exception as e:
        response.status = hug.falcon.HTTP_409
        return {"error": str(e)}

######## Change bio ########
@hug.put("/update-bio/")
def update_bio(
    response,
    username: hug.types.text,
    bio: hug.types.text,
    db: sqlite):
    try:
        db["users"].update(username, {"bio": bio})
    except Exception as e:
        response.status = hug.falcon.HTTP_409
        return {"error": str(e)}

######## Health check ########
@hug.get("/health-check/")
def health_check(response):
    return response.status
