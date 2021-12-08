# Members: Quang Nguyen, Vinh Tran
# CPSC 449
# Project 4: Asynchronous Processing

import hug
import configparser
import logging.config
import requests
import redis
import os
import socket

# Load configuration
#
config = configparser.ConfigParser()
config.read("./etc/like_service.ini")
logging.config.fileConfig(config["logging"]["config"], disable_existing_loggers=False)

@hug.startup()
def register(api):
    URL = "http://" + socket.getfqdn() + ":" + os.environ['PORT']
    payload = {'service': 'likes', 'URL': URL}
    requests.post(config["registry"]["URL"]+"/register-instance/", data = payload)

# Arguments to inject into route functions
#
@hug.directive()
def redisdb(section="redis", key="port", **kwargs):
    port = config[section][key]
    return redis.Redis(host="localhost", port=port)

@hug.directive()
def log(name=__name__, **kwargs):
    return logging.getLogger(name)

# Using Routes
######## Like a post ########
@hug.post("/like-post/")
def like_post(response,
    username: hug.types.text,
    post_id: hug.types.number,
    db: redisdb):
    if (db.sismember(username, post_id) == False):
        db.sadd(username, post_id)
        if (db.exists(post_id) == 1):
            db.incrby(post_id, 1)
            db.zincrby('pposts', 1, post_id)
        else:
            db.set(post_id, '1')
            db.zadd('pposts', {post_id : 1})


######## Show like of a post ########
@hug.get("/like-count/{post_id}")
def show_like_count(response, post_id: hug.types.number, db: redisdb):
    if (db.exists(post_id) == 1):
        return db.get(post_id)
    else:
        return {"post": 0}

######## Show posts that user liked ########
@hug.get("/user-liked/{username}")
def show_user_liked(username: hug.types.text, db: redisdb):
    return db.smembers(username)

######## Show popular posts ########
@hug.get("/popular-posts/")
def show_popular_posts(db: redisdb):
    posts = db.zrange('pposts', 0, 4, desc=True, withscores=True)
    return posts

######## Health check ########
@hug.get("/health-check/")
def health_check(response):
    return response.status
