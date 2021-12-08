# Members: Vinh Tran (Email: kimvinh@csu.fullerton.edu)
	   Quang Nguyen (Email: quangdnguyen2211@csu.fullerton.edu)

# CPSC 449 - 02

# Professor: Kenytt Avery

# Project 4: Asynchronous Processing

----------------------------------------------------------------------------------------------------

### SUMMARY ###

- There are two main microservices built in Project 2, one for 'users' and one for 'timelines' to provide
the services to users. With the 'users' services, users can register, follow/ unfollow each other, post messages,
and change their information (i.e., password, bio). With the 'timelines' services, they can show users' posts that
they have made, all posts from all users that this user followed, and all posts from all users. There are some
services that require users to log in before using.

- For all new creations related to 'user' or 'post' services, they will be stored in the database files. Each user created
will have a username, a bio, an email address, and a password. Each post that a user creates will have an id, the author's
username, the text (content) of the post, and a timestamp.

- There are three new microservices added in this project, one for 'like', one for 'poll', and one for 'service_registry'.
By using the 'like' services, users can like posts, view number of likes of a specfic post, get the list of posts that they
like, and see the top 5 popular posts that were liked by users. By using the 'poll' services, users can create a poll, vote a
specific poll once, and view the result of polls even though they do not vote. With the 'service_registry', each service instance
will be registered with their service name and a base URL for their endpoints. Moreover, a service instance can retrieve available instances
of another service.

- For all new creations related to the 'like' services, they will be stored in the NoSQL database named Redis. For likes database,
strings will be used to store the post_id (key) and number of likes, set will be use to store the username (key) and a set of liked
posts, sorted set will be used to store the post_id (key) and number of likes. The reason for using strings and sorted set to store
the post_id and number of likes is because it's easier to retrieve the data with strings, but it's easier to use the sorted set for
retreiving a list of posts in order. For all new creations of polls, they will be stored in the NoSQL database named "Amazon Dynamodb
Local". Each poll created will have an id as a primary key, an author, a question, at least 2 responses and at most 4 responses,
a 'voted_users' attribute that stores the information about voted users' username, and a 'voted_counts' attribute that stores the
number of votes corresponding to each choice of a poll.

- For production deployment, Gunicorn is used in this project as a WSGI server to run microservices, and the program was designed
to handle the running of multiple instances of the 'timeline' service by using HAProxy as an load balancer.

----------------------------------------------------------------------------------------------------

### MICROSERVICES - DETAILED DESCRIPTIONS ###

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

## 'Users' Microservices ##

1. @hug.startup()

- On startup, this service supports its instances being able to register their service name and base URL by using the registry service.

2. @hug.get("/users/")

- This service will return all existing users from the database as a JSON format.

- To use the service in the browser, please type URL = "http://127.0.0.1/users/"

- To use the service through the terminal, please command: $ http 127.0.0.1/users/

3. @hug.get("/users/{username}")

- This service will retrieve the specific user based on 'username' as the endpoint. If found, the response status will be '200 OK' and return the specific user as a JSON format. Otherwise, the response status is '404 NOT FOUND'.

- To use the service in the browser, please type URL = "http://127.0.0.1/users/{username}"

- To use the service through the terminal, please command: $ http 127.0.0.1/users/{username}

4. @hug.get("/get-following/{username}")

- This service retrieves all users that a user follows based on 'username' as the endpoint from the databbase. Users will be returned as a JSON format.

- To use the service in the browser, please type URL = "http://127.0.0.1/get-following/{username}"

- To use the service through the terminal, please command: $ http 127.0.0.1/get-following/{username}

5. @hug.post("/create/", status=hug.falcon.HTTP_201)

- This service allows a user to create an account. A user's account will include a username, an email, a password, and a bio. If created successfully, the response status is '201 Created'. Otherwise, the response status is '409 Conflict' if a user tries to create an account that was already existed, and the error message will be returned.

- To use the service through the terminal, please use 'new_user.json' as an example.
In the terminal, please command: $ http --verbose POST 127.0.0.1/create/ @./share/new_user.json

6. @hug.put("/change-password/")

- This service allows an existing user to change their password. If changed successfully, the response status is ' 200 OK'. Otherwise, the response status is either '401 Unauthorized' or '404 Not Found' if inputs are incorrect.

- To use the service through the terminal, please use 'new_password.json' as an example.
In the terminal, please command: $ http --verbose PUT 127.0.0.1/change-password/ @./share/new_password.json

7. @hug.get("/login/")

- This service will verify the user's authentication by checking a user's username and password. If a user successfully logs in, they can access to some services that require the authentication. Otherwise, the response status is either '401 Unauthorized' or '404 Not Found' if inputs are incorrect, and the error message will be returned.

- To use the service in the browser, please type URL = "http://127.0.0.1/login?username={username}&password={password}"

- To use the service through the terminal, please command: http '127.0.0.1/login?username={username}&password={password}'

8. @hug.post("/follow/", status=hug.falcon.HTTP_201)

- This service allows an existing user to follow each other. If followed successfully, the response status is '201 Created'. Otherwise, the response status is '409 Conflict' if a user tries to follow another user that they already followed.

- To use the service through the terminal, please use 'new_follow.json' as an example.
In the terminal, please command: $ http --verbose POST 127.0.0.1/follow/ @./share/new_follow.json

9. @hug.post("/unfollow/")

- This service allows an existing user to unfollow each other. A user needs to provide their username and another user's username that they want to unfollow. If unfollowed successfully, the response status is '200 OK'. Otherwise, the response status is '409 Conflict' if a user tries to unfollow another user that they do not follow yet.

- To use the service through the terminal, please use 'new_follow.json' as an example.
In the terminal, please command: $ http --verbose POST 127.0.0.1/unfollow/ @./share/new_follow.json

10. @hug.put("/update-bio/")

- This service allows an existing user to update their bio. They need to provide their username and the text for their bio. If updated successfully, the response status is '200 OK'. Otherwise, the response status is '400 Bad Request' if inputs are incorrect or missing.

- To use the service through the terminal, please use 'new_bio.json' as an example.
In the terminal, please command: $ http --verbose PUT 127.0.0.1/update-bio/ @./share/new_bio.json

11. @hug.get("/health-check/")

- This service is to support the health check for checking if its instances are still working. It will be called by the registry service.

- Endpoint: /health-check/

- HTTP Method: GET

- HTTP Response Status Codes:
  + '200 OK' if the instances are still working.

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

## 'Timelines' Microservices ##

1. @hug.startup()

- On startup, this service supports its instances being able to register their service name and base URL by using the registry service.

2. @hug.get("/post/")

- This service will return all users' posts from the database as a JSON format.

To use the service in the browser, please type URL = "http://127.0.0.1/posts/"

To use the service through the terminal, please command: $ http 127.0.0.1/posts/

3. @hug.get("/userTimeline/{username}")

- This service will provide a user timeline by retrieving all posts that a user has made based on 'username' as the endpoint. If retrieved successfully, the response status is '200 OK', and all posts will be returned as a JSON format by the reverse chronological order. Otherwise, the response status is '404 Not Found' if the input is not correct, and the returned post is empty.

To use the service in the browser, please type URL = "http://127.0.0.1/userTimeline/{username}"

To use the service through the terminal, please command: $ http 127.0.0.1/userTimeline/{username}

4. @hug.get("/publicTimeline/")

- This service will retrieve all users' posts and return them in the reverse chronological order as a public timeline. If retrieved successfully, the response status is '200 OK', and all posts will be returned as a JSON format. Otherwise, the response status is '404 Not Found', and the returned post is empty.

To use the service in the browser, please type URL = "http://127.0.0.1/publicTimeline/"

To use the service through the terminal, please command: $ http 127.0.0.1/publicTimeline/

5. @hug.get("/homeTimeline/{username}", requires=authentication)

- This service allows an existing user to see all users' posts that they followed as a home timeline. However, they need to get the authorization to use the service by logging in. Also, they can only access their home timeline to themselves. If authenticated successfully, all users' posts that a user followed will be returned as a JSON format in the reverse chronological order. Otherwise, the response status is '404 Not Found' if an input is not correct, and the returned post is empty.

To use the service in the browser, please type URL = "http://127.0.0.1/homeTimeline/{username}"

To use the service through the terminal, please command: $ http --auth username:password 127.0.0.1/homeTimeline/{username}

6. @hug.post("/message/", requires=authentication)

- This service allows an existing user to post messages, but they need to get the authorization to do so by logging in and then input the text for the post. If authenticated successfully and inputted correctly, the response status is '201 Created', and the post will be returned as a JSON format. Otherwise, the response status is either '401 Unauthorized' due to the failure of login or '400 Bad Request' if the input is incorrect or missing.

To use the service through the terminal, please command: $ http --auth username:password POST 127.0.0.1/message/ text="{The text of the post}"

7. @hug.get("/health-check/")

- This service is to support the health check for checking if its instances are still working. It will be called by the registry service.

- Endpoint: /health-check/

- HTTP Method: GET

- HTTP Response Status Codes:
  + '200 OK' if the instances are still working.

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

## 'Poll' Microservices  ##

1. @hug.startup()

- On startup, this service supports its instances being able to register their service name and base URL by using the registry service.

2. @hug.post("/polls/create/", status=hug.falcon.HTTP_201)

- This service allows any users to create a poll.

- Endpoint: /polls/create/

- HTTP Method: POST

- HTTP Response Status Codes:
  + '201 Created' if successfully created by providing valid inputs.
  + '400 Bad Request' if users provide invalid inputs.
  + '409 Conflict' if an user attempts to create two polls with the same id.

- To use the service through the terminal, please use 'new_poll.json' as an example.
In the terminal, please command: $ http --verbose POST 127.0.0.1:5400/polls/create/ @./share/new_poll.json

Or,

In the terminal, please command: $ http POST 127.0.0.1:5400/polls/create/ poll_id={id} created_by={username} question={"The text of a question of the poll"} poll_responses={"Option1, Option2, Option3, Option4"}

3. @hug.put("/polls/vote/{id}")

- This service allows any users to vote a specific poll based on its id.

- Endpoint: /polls/vote/{id}

- HTTP Method: PUT

- HTTP Response Status Codes:
  + '200 OK' if successfully voted by providing correct id and valid choice
  + '400 Bad Request' if an users provided invalid choice to vote
  + '404 Not Found' if an users provided incorrect id of the poll
  + '409 Conflict' if an users attemps to vote the same poll twice

- To use the service through the terminal, please command: $ http PUT 127.0.0.1:5400/polls/vote/{id} username={username} choice={valid_choice}

4. @hug.get("/polls/view-result/{id}")

- This service allows any users to view the result of a specific poll based on its id.

- Endpoint: /polls/view-result/{id}

- HTTP Method: GET

- HTTP Response Status Codes:
  + '200 OK' if successfully viewed the result by providing correct id
  + '404 Not Found' if an user provided incorrect id of the poll

- To use the service in the browser, please type URL = "http://127.0.0.1:5400/polls/view-result/{id}"

- To use the service through the terminal, please command: $ http 127.0.0.1:5400/polls/view-result/{id}

5. @hug.get("/health-check/")

- This service is to support the health check for checking if its instances are still working. It will be called by the registry service.

- Endpoint: /health-check/

- HTTP Method: GET

- HTTP Response Status Codes:
  + '200 OK' if the instances are still working.

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

## 'Like' Microservices ##

1. @hug.startup()

- On startup, this service supports its instances being able to register their service name and base URL by using the registry service.

2. @hug.post("/like-post/")

- This service allows any users to like a post.

- Endpoint: /like-post/

- HTTP Method: POST

- HTTP Response Status Codes:
  + '201 Created' when successfuly increase the # of likes of the post by 1, and add the post_id to the set of posts that user liked

- To use the service through the terminal, please command: http POST 127.0.0.1:5300/like-post username={username} post_id={post_id}

3. @hug.get("/like-count/{post_id}")

- This service allows any users to view number of likes of a specific post.

- Endpoint: /like-count/{post_id}

- HTTP Method: GET

- HTTP Response Status Codes:
  + '200 OK' if successfully viewed number of likes of a post by providing a valid id.

- To use the service in the browser, please type URL = "http://127.0.0.1:5300/like-count/{post_id}"

- To use the service through the terminal, please command: $ http 127.0.0.1:5300/like-count/{post_id}

4. @hug.get("/user-liked/{username}")

- This service allows users to see posts that they or other people liked.

- Endpoint: /user-liked/{username}

- HTTP Method: GET

- HTTP Response Status Codes:
  + '200 OK' if successfully return the number of posts that user liked

- To use the service in the browser, please type URL = "http://127.0.0.1:5300/user-liked/{username}"

- To use the service through the terminal, please command: $ http 127.0.0.1:5300/user-liked/{username}

5. @hug.get("/popular-posts/")

- This service allows users to see top 5 popular posts that were liked by them or others.

- Endpoint: /popular-posts/

- HTTP Method: GET

- HTTP Response Status Codes:
  + '200 OK' if successfully see top 5 popular posts

- To use the service in the browser, please type URL = "http://127.0.0.1:5300/popular-posts"

- To use the service through the terminal, please command: $ http 127.0.0.1:5300/popular-posts

6. @hug.get("/health-check/")

- This service is to support the health check for checking if its instances are still working. It will be called by the registry service.

- Endpoint: /health-check/

- HTTP Method: GET

- HTTP Response Status Codes:
  + '200 OK' if the instances are still working.

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

## 'Service Registry' Microservices ##

1. @hug.startup()

- This service is considered the health check. It automatically starts its task whenever the registry service begins. Its task is to create a daemon thread to continuously check the status of other services' instances to see if they are up or down.

- If one of any services' instances is down, the service will remove it from the service registry.

2. @hug.get("/{service}/")

- This service allows users to retrieve all registered instances of a specific service in the service registry.

- Endpoint: /{service}/

- HTTP Method: GET

- HTTP Response Status Codes:
  + '200 OK' if successfully return the lists of all registered instances of a service in the registry.
  + '404 Not Found' if there are no registered instances returned.

- To use the service in the browser, please type URL = "http://127.0.0.1:5000/{service}"

- To use the service through the terminal, please command: $ http 127.0.0.1:5000/{service}

3. @hug.post("/register-instance/")

- This service supports any services to register their instances if any and puts all registered instances into the service registry. The service will be automatically called by other services when users start using one of their URLs.

- Endpoint: /register-instance/

- HTTP Method: POST

- HTTP Response Status Codes:
  + '200 OK' if successfully support a service to register their instances and put them into the registry
  + '409 Conflict' if there is a service attempting to register a instance which is already registered.

----------------------------------------------------------------------------------------------------

### REQUIREMENTS ###

- There are some tools, libraries, and NoSQL databases needed to be installed before running the microservices:

   1. Hug
   2. sqlite-utils libraries
   3. HAProxy
   4. Gunicorn server
   5. Amazon Dynamodb Local
      Link to downdload: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html
   6. AWS CLI
   7. Redis
   8. Python libraries for Redis
   9. Boto3 library

----------------------------------------------------------------------------------------------------

### "CPSC-449-Project3.tar.gz" Contents ###

1. README.txt				// This file

2. timelines_services.py		// Containing the source code that executes the 'timelines' services

3. user_services.py			// Containing the source code that executes the 'users' services

4. poll_services.py			// Containing the source code that executes the 'poll' services

5. like_service.py			// Containing the source code that executes the 'like' services

6. service_registry.py			// Containing the source code that executes the service registry

7. create_polls_table.py			// Containing the source code that executes the creation of 'polls' table in local Dynamodb

8. Profile				// Containing The WSGI-compatible server (Gunicorn) to run both microservices

9. .env				// Avoiding missing output from Foreman

10. "var" folder			// Containing the log and database files
   10.1. "log" folder			// Containing the log files of microservices
      10.1.1. user_services.log		// Containing records of activities within the 'users' microservice
      10.1.2. timelines_services.log	// Containing records of activities within the 'timelines' microservice
      10.1.3. poll_services.log	// Containing records of activities within the 'poll' microservice
      10.1.4. service_registry.log	// Containing records of activities within the 'like' microservice
   10.2. posts.db			// The database file that stores all users' posts
   10.3. users.db			// The database file that stores all users' information and followings

11. "bin" folder				// Containing the shell files
   11.1. init.sh				// The shell script that initializes all database files
   11.2. posts.sh			// The shell script that run the specific command(s)

12. "etc" folder				// Containing the configuration files related to two microservices
   12.1. users_services.ini
   12.2. timelines_services.ini
   12.3. user_services_logging.ini
   12.4. timelines_services_logging.ini
   12.5. like_service.ini
   12.6. like_service_logging.ini
   12.7. poll_services.ini
   12.8. poll_services_logging.ini
   12.9. service_registry.ini
   12.10. service_registry_logging.ini
   12.11. haproxy.cfg

13. "share" folder			// Containing the JSON and CSV files
   13.1. new_bio.json
   13.2. new_follow.json
   13.3. new_password.json
   13.4. new_user.json
   13.5. new_poll.json
   13.6. following.csv
   13.7. posts.csv
   13.8. users.csv

----------------------------------------------------------------------------------------------------

### INSTALLATION AND SETUP ###

# Note: The following steps will ask you to install some tools and libraries to meet the requirements
for running the project.

1. To install pip package installer and tools, command:

$ sudo apt update
$ sudo apt install --yes python3-pip ruby-foreman httpie sqlite3

2. To install Hug and sqlite-utils libraries, command:

$ python3 -m pip install hug sqlite-utils

3. To install the HAProxy and Gunicorn servers, command:

$ sudo apt install --yes haproxy gunicorn

4. To install Redis, command:

$ sudo apt install --yes redis

5. (Optional) To verify that Redis is installed and working, command:

$ redis-cli ping

Expected Output: PONG

6. To install Python libraries for Redis, command:

$ sudo apt install --yes python3-hiredis

7. To install Boto3 library, command:

$ sudo apt install --yes python3-boto3

8. To install the AWS CLI to prepare for running aws configure, command on another terminal:

$ sudo apt install --yes awscli

9. Assume that you downloaded, extracted, and moved the contents of Amazon Dynamodb to a location of your choice (if not, please see 'REQUIREMENTS' section to download), to run Amazon Dynamodb locally, change the current directory to the one that contains "DynamoDB.jar", and command:

$ java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb

Expected Output:

Initializing DynamoDB Local with the following configuration:
Port:	8000
InMemory:	false
DbPath:	null
SharedDb:	true
shouldDelayTransientStatuses:	false
CorsParams:	*

10. To run aws configure, command and input on another terminal:

$ aws configure
AWS Access Key ID [None]: fakeMyKeyId
AWS Secret Access Key [None]: fakeSecretAccessKey
Default region name [None]: us-west-2
Default output format [None]: table

11. To create 'polls' table for the 'poll' service stored in Dynamodb, command:

$ python3 create_polls_table.py

Expected Output:

Table status: ACTIVE

12. To load the database for the 'users' and 'posts' services, command:

$ ./bin/init.sh

13. Please replace the content of 'haproxy.cfg' file in your system with the content of 'haproxy.cfg' in the "etc" folder.

### HOW TO START THE SERVICES ###

# Note: Please finish all steps from 'INSTALLATION AND SETUP' section to avoid any errors, bugs, or failures before running the services by following steps below.

1. Run AWS Dynamodb locally, please follow the step #9 in 'INSTALLATION AND SETUP' section.

2. To configure HAProxy to present as an HTTP load balancer, command on another terminal:

$ sudo systemctl start haproxy

3. To start microservices concurrently, command on the terminal:

$ foreman start --formation service_registry=1,user_services=1,timelines_services=3,like_service=1,poll_services=1

4. To begin using the services, please open another terminal and read 'MICROSERVICES - DETAILED DESCRIPTIONS' section for more detail.
