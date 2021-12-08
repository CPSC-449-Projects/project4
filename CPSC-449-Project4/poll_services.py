# Members: Quang Nguyen, Vinh Tran
# CPSC 449
# Project 4: Asynchronous Processing

import hug
import boto3
import json
import configparser
import logging.config
import requests
import os
import socket



''' Load Dynamodb locally '''
dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
table = dynamodb.Table('polls')

''' Load Configuration '''
config = configparser.ConfigParser()
config.read("./etc/poll_services.ini")
logging.config.fileConfig(config["logging"]["config"], disable_existing_loggers=False)

@hug.startup()
def register(api):
    URL = "http://" + socket.getfqdn() + ":" + os.environ['PORT']
    payload = {'service': 'polls', 'URL': URL}
    requests.post(config["registry"]["URL"]+"/register-instance/", data = payload)

''' Arguments to inject into route functions '''
@hug.directive()
def sqlite(section="sqlite", key="dbfile", **kwargs):
    dbfile = config[section][key]
    return sqlite_utils.Database(dbfile)

@hug.directive()
def log(name=__name__, **kwargs):
    return logging.getLogger(name)

''' Design the function that returns a specific poll based on its id '''
@hug.get("/polls/{id}")
def retrieve_poll(id: hug.types.number):
    try:
        data = table.get_item(
            Key = { "poll_id": id }
        )
        poll = data['Item']
    except:
        return {}
    return poll

# Router

''' Design the service that deletes a specific poll based on its id '''
@hug.delete("/polls/delete/{poll_id}")
def delete_item(response, poll_id: hug.types.number):
    try:
        table.delete_item(
            Key={"poll_id": poll_id}
        )
    except:
        response.status = hug.falcon.HTTP_404
    return response.status

''' Design the service that creates a new poll '''
@hug.post("/polls/create/", status=hug.falcon.HTTP_201)
def create_poll(response,
                poll_id: hug.types.number,
                created_by: hug.types.text,
                question: hug.types.text,
                poll_responses):

    # Only execute if an user uses command line to input responses for a poll
    # Otherwise, skip this code
    if type(poll_responses) == str:
        poll_responses = poll_responses.split(', ')

    # The number of valid responses of a poll should be in the range of 2 to 4
    # Otherwise, raise the error
    if len(poll_responses) < 2:
        response.status = hug.falcon.HTTP_400
        return {"error": "A poll should have at least 2 responses"}
    elif len(poll_responses) > 4:
        response.status = hug.falcon.HTTP_400
        return {"error": "A poll should only have at most 4 responses"}

    # Initialize the attributes for a poll
    voted_users = {}
    voted_counts = {}

    # Assign the default values to the attributes
    for i in poll_responses:
        voted_users.update({f'{i}': []})
        voted_counts.update({f'{i}': 0})

    # Put the poll into the database
    # Note: If an user are attempting to create a poll whose id already exists, they don't allow
    try:
        table.put_item(Item={
            "poll_id": poll_id,
            "created_by": created_by,
            "question": question,
            "responses": poll_responses,
            "voted_users": voted_users,
            "voted_counts": voted_counts
        }, ConditionExpression='attribute_not_exists(poll_id)')
    except Exception as e:
        data = table.scan()
        polls = data['Items']
        while 'LastEvaluatedKey' in data:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            polls.extend(response['Items'])
        e = f'poll_id already exists. You may use poll_id = {len(polls)+1}'
        response.status = hug.falcon.HTTP_409
        return {"error": str(e)}
    return response.status

''' Design the service that allows users to vote '''
# Note: Each user is allowed to vote once
@hug.put("/polls/vote/{id}")
def vote_poll(response, id: hug.types.number,
              username: hug.types.text,
              choice: hug.types.text):

    # Retrieve the specific poll
    poll = retrieve_poll(id)
    if poll == {}:
        response.status = hug.falcon.HTTP_404
        return {"error": "No Target Poll Found"}

    valid_choice = False

    # Check if an user's choice is valid
    # Also check if an user voted
    for i in poll['responses']:
        if i == choice:
            valid_choice = True
            for user in poll['voted_users'][choice]:
                if user == username:
                    response.status = hug.falcon.HTTP_409
                    return {"error": "You already voted."}
            break

    # Update the new values to the poll if the input is valid
    if valid_choice == True:
        poll['voted_users'][choice].append(username)
        poll['voted_counts'][choice] += 1
    else:
        response.status = hug.falcon.HTTP_400
        return {"error": "Your choice may be invalid. Please check and try again."}

    # Update the poll in the database
    table.put_item(Item=poll)
    return response.status

''' Design the service that allows users to view the result of a specific poll '''
# Note: Any user can view even though they don't vote
@hug.get("/polls/view-result/{id}")
def result(response, id: hug.types.number):
    poll = retrieve_poll(id)
    if poll == {}:
        response.status = hug.falcon.HTTP_404
        return {"error": "No Target Poll Found"}
    return poll

@hug.get("/health-check/")
def health_check(response):
    return response.status
