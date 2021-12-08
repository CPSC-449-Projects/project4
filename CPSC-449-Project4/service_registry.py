# Members: Quang Nguyen, Vinh Tran
# CPSC 449
# Project 4: Asynchronous Processing


import hug
import configparser
import logging.config
import requests
import time
import threading
import concurrent.futures
import os
import socket

lock = threading.Lock()
registered_services = {
    "users": [],
    "posts": [],
    "likes": [],
    "polls": []
}

# Load configuration
#
config = configparser.ConfigParser()
config.read("./etc/service_registry.ini")
logging.config.fileConfig(config["logging"]["config"], disable_existing_loggers=False)

def health_check():
    while 1:
        for i in registered_services:
            for j in registered_services[i]:
                print("[CHECKING]", j)
                try:
                    r = requests.get(j + "/health-check/")
                    # Scenario #1
                    # Check one of each service's URLs
                    # If it returns a status code other than '200 OK', then remove it
                    if r.status_code != 200:
                        print(f'[REMOVED] {j}')
                        # Using basic synchronization lock to prevent race condition
                        with lock:
                            registered_services[i].remove(j)
                    print(f'[{r.status_code}] {j}\n')
                except requests.ConnectionError:
                    # Scenario #2
                    # If one of each service's instances is down, then remove it
                    # Using basic synchronization lock to prevent race condition
                    with lock:
                        registered_services[i].remove(j)
                    print(f'[CONNECTION FAILED] {j}')
                    print(f'[REMOVED] {j}\n')
        time.sleep(5)

@hug.startup()
def startup(api=None):
    myThread = threading.Thread(target=health_check, daemon=True)
    myThread.start()

# Arguments to inject into route functions
@hug.directive()
def log(name=__name__, **kwargs):
    return logging.getLogger(name)

@hug.get("/{service}/")
def get_services(service: hug.types.text):
    services = []
    try:
        for i in registered_services[service]:
            services.append(i)
    except Exception as e:
        response.status = hug.falcon.HTTP_404
    return services

######## Register service instance ########
@hug.post("/register-instance/", status=hug.falcon.HTTP_201)
def register_intances(request,response,
    service: hug.types.text,
    URL: hug.types.text):
    try:
        registered_services[service].append(URL)
    except Exception as e:
        response.status = hug.falcon.HTTP_409
        return {"error": str(e)}
