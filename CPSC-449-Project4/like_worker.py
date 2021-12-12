# Members: Quang Nguyen, Vinh Tran
# CPSC 449
# Project 4: Asynchronous Processing

import configparser
import logging.config
import requests
import redis
import sqlite_utils
import greenstalk
import json
import smtplib
from smtplib import SMTPException

config = configparser.ConfigParser()
config.read("./etc/like_worker.ini")
host = config["host"]["localhost"]
email_port = config["email"]["port"]
postdb = config["sqlite"]["dbfile"]
redisdb = redis.Redis(host="localhost", port=config["redis"]["port"])
address = (host, 8000)

# Initializing the sender and receiver email
sender = 'Group4@server.com'
receiver = 'Group4@server.com'

with greenstalk.Client(address, encoding='utf-8', use='default', watch='default') as client:
    while True:
        # Getting the username and the post id
        job = client.reserve()
        job_body = json.loads(job.body)

        try:
                # Testing if the post is valid
                post = sqlite_utils.Database(postdb)["post"].get(job_body["post_id"])

        except sqlite_utils.db.NotFoundError:
                # Removing the invalid post
                redisdb.delete(job_body["post_id"])
                redisdb.srem(job_body["username"], job_body["post_id"])
                redisdb.zrem('pposts', job_body["post_id"])

                # Retrieving user's email
                r = requests.get(f'http://127.0.0.1/users/{job_body["username"]}')
                replies = r.json()
                receiver = replies["users"][0]["email_address"]

                # Constructing the email
                message = "From: " + sender + "\nTo: " + receiver + """\nSubject: Invalid Like
                    The post that you liked is invalid because it is not in the database."""

                # Trying to send the email
                try:
                   smtpObj = smtplib.SMTP(host, email_port)
                   smtpObj.sendmail(sender, receiver, message)
                   print("Successfully sent email")
                except SMTPException:
                   print("Error: unable to send email")

        # Deleting the job
        client.delete(job)

# hey -n 1 -c 1 -m POST -H "Authorization: Basic dmluaHRyYW46Y3J5" -d '{"username":"vinhtran","text":"bruh"}' -T "application/json" "http://127.0.0.1/message"
