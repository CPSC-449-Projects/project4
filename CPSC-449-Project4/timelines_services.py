# Members: Quang Nguyen, Vinh Tran
# CPSC 449
# Project 4: Asynchronous Processing


import hug
import sqlite_utils
import datetime
import configparser
import logging.config
import requests
import os
import socket
import greenstalk
import json
import re


# Load configuration
#
config = configparser.ConfigParser()
config.read("./etc/timelines_services.ini")
logging.config.fileConfig(config["logging"]["config"], disable_existing_loggers=False)

@hug.startup()
def register(api):
    URL = "http://" + socket.getfqdn() + ":" + os.environ['PORT']
    payload = {'service': 'posts', 'URL': URL}
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
@hug.get("/posts/")
def posts(db: sqlite):
    return {"post": db["post"].rows}

''' Design the service of user timeline '''
@hug.get("/userTimeline/{username}")
def retrieveUserTimeline(response, username: hug.types.text, db: sqlite):
    posts = []
    try:
    	for post in db.query("SELECT * FROM post WHERE username = ? ORDER BY timestamp DESC", [username]):
        	posts.append(post)
    except sqlite_utils.db.NotFoundError:
        response.status = hug.falcon.HTTP_404
    return {"post": posts}

''' Design the service of public timeline '''
@hug.get("/publicTimeline/")
def retrievePublicTimeline(response, db: sqlite):
    posts = []
    try:
        for post in db.query("SELECT * FROM post ORDER BY timestamp DESC"):
            posts.append(post)
    except sqlite_utils.db.NotFoundError:
        response.status = hug.falcon.HTTP_404
    return {"post": posts}

def check_user(username, password):
    r1 = requests.get(config["registry"]["URL"]+"/users")
    service_URL = r1.json()

    # Check if the users service is working
    # If not, return HTTP Status Code = 502 as Bad Gateway
    if len(service_URL) == 0:
        return 502

    payload={'username': username, 'password': password}
    r2 = requests.get(service_URL[0]+"/login", params=payload)
    if r2.status_code == 200:
        return username

authentication=hug.authentication.basic(check_user)

''' Design the service of home timeline '''
@hug.get("/homeTimeline/{username}", requires=authentication)
def retrieveHomeTimeline(response, username: hug.types.text, info: hug.directives.user, db: sqlite):
    # Check the return value of 'info'
    # If 'info' has a value of 502 as HTTP Status Code.
    # That means the users service is not ready. Then show the error as 502 Bad Gateway
    # If 'info' has a value of a username of an user. Then compare it with an user's input
    if info == 502:
        response.status = hug.falcon.HTTP_502
        return {'error': '502 Bad Gateway'}
    elif username != info:
        response.status = hug.falcon.HTTP_404
        return {"error": f"You are unauthorized to access the home timeline of {username}."}

    follows = []
    r1 = requests.get(config["registry"]["URL"]+"/users")
    service_URL = r1.json()

    list_of_followings = requests.get(service_URL[0]+f'/get-following/{username}')
    list_of_followings = list_of_followings.json()

    for following in list_of_followings["follows"]:
        follows.append(following["following"])

    # Create number of bind parameters as '?' based on the length of the list 'follows'
    bindParameters = ""
    for i in range(len(follows)):
        bindParameters += '?'

    # Format properly the string of 'bindParameters' into ?, ?, ?, ..., ? to be used in the database query
    bindParameters = ', '.join(bindParameters)

    posts = []
    try:
        for post in db.query(f"SELECT * FROM post WHERE username IN ({bindParameters}) ORDER BY timestamp DESC", follows):
            posts.append(post)
    except sqlite_utils.db.NotFoundError:
        response.status = hug.falcon.HTTP_404

    return {"post": posts}

''' Design the service of allowing an existing user to post a message '''
@hug.post("/message/", requires=authentication)
def postMessage(response, username: hug.directives.user, text: hug.types.text, db: sqlite):
    if username == 502:
        response.status = hug.falcon.HTTP_502
        return {'error': '502 Bad Gateway'}

    posts = db["post"]

    post = {
        "username": username,
        "text": text,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        posts.insert(post)
        post["id"] = posts.last_pk
    except Exception as e:
        response.status = hug.falcon.HTTP_409
        return {"error": str(e)}

    response.set_header("Location", f"/posts/{post['id']}")
    return post

@hug.post("/message/asyn/", requires=authentication, status=hug.falcon.HTTP_202)
def asynPostMessage(response, username: hug.directives.user, text: hug.types.text):
    if username == 502:
        response.status = hug.falcon.HTTP_502
        return {'error': '502 Bad Gateway'}

    client = greenstalk.Client(('127.0.0.1', 11300))
    post = {
        "username": username,
        "text": text,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    post = json.dumps(post)
    client.put(post)


''' Design the service of retrieving a specific post based on its ID '''
@hug.get("/posts/{id}")
def retrieve_post(response, id: hug.types.number, db:sqlite):
    posts = []
    try:
        post = db["post"].get(id)
        posts.append(post)
    except sqlite_utils.db.NotFoundError:
        response.status = hug.falcon.HTTP_404
    return {"posts": posts}

######## Health check ########
@hug.get("/health-check/")
def health_check(response):
    return response.status
