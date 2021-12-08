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
import greenstalk
import json

# Load configuration
#
config = configparser.ConfigParser()
config.read("./etc/timelines_services.ini")
logging.config.fileConfig(config["logging"]["config"], disable_existing_loggers=False)

# Arguments to inject into route functions
#
@hug.directive()
def sqlite(section="sqlite", key="dbfile", **kwargs):
    dbfile = config[section][key]
    return sqlite_utils.Database(dbfile)

@hug.directive()
def log(name=__name__, **kwargs):
    return logging.getLogger(name)

@hug.post("/consume/")
def consumer(response, db: sqlite):
    print("Hello")
    client = greenstalk.Client(('127.0.0.1', 11300))
    job = client.reserve()
    post = json.loads(job.body)

    posts = db["post"]
    try:
        posts.insert(post)
        post["id"] = posts.last_pk
    except Exception as e:
        response.status = hug.falcon.HTTP_409
        return {"error": str(e)}

    client.delete(job)
    response.set_header("Location", f"/posts/{post['id']}")
    return post
