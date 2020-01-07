# Learn flaskRESTful Development and Deployment

## Overview

This repo provides sample code for a todo list api that uses the flaskRESTful framework, flask JWT for user authentication, and mongodb as a document based data base.

Through this README and the rest of the repository, you will find detailed explanations for all code and a walkghrough on how to deploy this api to heroku.

## Prerequisites

- Basic understanding of python syntax

- Basic understanding of object oriented programming

- Basic understanding of HTTP and what the different methods are:

  - GET: get a resource
  - POST: create a resource
  - PUT: update a resource
  - DELETE: delete a resource

- Basic understanding of git

## Environment Setup

### Github ([Join](https://github.com/join)) and Git ([Installation](https://git-scm.com/downloads))

In order to deploy to Heroku, the source code will be pulled from Github. For this you will need to install git on your computer and create a Github account.

- Note: Macs already come with git installed!

### Python 3 ([Installation](https://realpython.com/installing-python/))

Flask is a python framework; therefor, you will need python to develop and run it.

### MongoDB ([Windows Installation](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/)) ([Mac Installation](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/))

MongoDB is a no SQL database that is made of collections that contain documents. The structure of these documents is similar to that of a python dictionary or a [JSON](https://www.w3schools.com/js/js_json_intro.asp). For development on your machine, you will need a local instance of MongoDB.

We will be using this database for our flask application. Our app will create and add to a collection called users and a collection called todos. A document in users will represent a user and a document in todos will represent a todo.

- Note: To install MongoDB on mac, you may need to install the [Homebrew](https://brew.sh/) package manager if you have not already!

### Virtual Env ([Installation](https://virtualenv.pypa.io/en/latest/installation/))

VirtualEnv is a python module that allows you to create a special directory to hold all of your projects dependencies. Ex. flask, flaskJWT, flaskpymongo. In order for you to create VirtaulEnvs for your projects, use the python package manager, pip, to install virtualenv.

We use virtualenv because we want to have a seperate set of dependencies for each project. This is because some projects have the same dependencies, but rely on different vesrions. If we were pulling the dependencies from the same place, we could only have one of those versions at a time.

### Postman ([Installation](https://www.getpostman.com/downloads/))

Postman is a great tool that allows us to test each endpoint of our API in development and in production. Install postman so that you can test the enpoints of your api as well.

## Dependency Walk-through

### FlaskRESTful ([Documentation](https://flask-restful.readthedocs.io/en/latest/))

- Flask

  - Micro web framework written in Python
  - Lightweight and flexible allowing developers lots of control over design and implementation

- Flask-RESTful

  - An extension of Flask that helps developers build APIs that follow REST principles faster
  - Allows you to create resource classes that have HTTP methods as member functions

**All overided HTTP methods in Flask-RESTful resources must take the exact same arguments**

### Flask-JWT/ Flask-JWT-Extended ([Documentation](https://flask-jwt-extended.readthedocs.io/en/stable/))

Allows your application to handle user authentication by issuing a user an auth and refresh token that must be sent each time the user makes a request to the API that requires authentication.

After a given amount of time, the session experises and the user must get a new authtoken by logging in again or refreshing with their refresh token.

More on this later and in the code itself!

### Flask-PyMongo ([Documentation](https://flask-pymongo.readthedocs.io/en/latest/))

This is a module that allows your app to talk to a MongoDB database directly from python. This will be used liberally in the code.

## Code Walk-through

### requirements.txt

This file lists all of the dependencies for this project. It is used to install all of the correct python packages into the VirtualEnv upon creation. We will go over this more in the next section.

This file is also used by heroku for deployment when installing dependencies on their servers.

- Note: The uwsgi dependency is not needed for local development and will often cause an error if you try and download it on your machine. You can delete it for now but remember to put it back when you are deploying.

### app.py

This is where the initial magic happens!

- Create a Flask app called app

- Add key value pairs to the config dict inside of app

  - Each is explained in the code via comments

- Create a flaskRESTful api by passing the app into the Api constructor

- Create a JWT authentication manager by passing app into the JWTManager constructor

- Use jwt decorators to define callbacks for jwt behaviours in certain situations

  - Each is explained in the code via comments

- Add resources to the api

  - api.add_resource takes the definition of the Resource class declared in the resources directory and the endpoint that resource's methods will be able to be called from

- Initialize mongodb session and run app **only if the variable \_\_name\_\_ is equal to "\_\_main\_\_"**
  - This is only true when running the server locally during development
  - In production, run.py is executed instead

### db.py

Creates a PyMongo client that is used to establish a session when it is imported in app.py or run.py and mongo.init_app(app) is called.

### blacklist.py

Creates a set that holds blacklisted auth and refresh tokens. It is used in functions like check_if_token_in_blacklist().

### /resources

This holds all of the defined resources for the API. They are all subclasses of flaskRESTful's Resource class. Each of these resource classes can overide any of the HTTP methods.

#### \_\_init\_\_.py

- This file is blank and may not seem necessary, but it is very important to the structure of this project.

- In python all import statements start from the root of the project directory.

- The root of this project directory is where app.py is.

- All import statements start from the root. This means that regardless of where you are importing something like the TodoRegister, you would have to do this:
  `from resources.todo import TodoRegister`

- There should be a \_\_init.py\_\_ file like this in any subdirectory of a flask project.

#### user.py

The user file is where the creation, login, and logout of users generally takes place.

**Refer to comments in code for more specific explanations of syntax, etc.**

- UserRegister
  `{url}/register`

  - This resource is used to create new users in the users collection within the MongoDB database
  - Because this resource is only used for creating users, it only implements the post method

- User
  `{url}/user/<string:username>`

  - This resource is used to get and delete users and is generally intended for testing
  - In production, you would not want an endpoint like this to be public

- UserLogin
  `{url}/login`

  - This is used to login a user.
  - The post request will use the \_user_parser to parse the body of the HTTP request being sent to the webserver.
  - The arguments from the body will be used to check if the usernam is valid and the password is correct
  - If the previous are correct, a access_token and a refresh_token are sent to the caller
  - The caller will use the access_token as the value for the Authorization HTTP header to make requests to the endpoints with the @jwt_required decorator
  - When the session expires, the caller can use the refresh_token as the value for the Authorization HTTP header to get back a new

- UserLogout
  `{url}/logout`

  - This resource is used to logout the current user
  - When the caller wants to logout, the caller will use the access_token as the value for the Authorization HTTP header, so that their JWT id can be added to the blacklist and there session will be over

- TokenRefresh
  `{url}/refresh`

  - This resource is used to get a new access_token when the callers session has expired
  - When the session expires, the caller can use the refresh_token as the value for the Authorization HTTP header and get back a newly generater access_token

#### todo.py

### .gitignore

This lists all of the files that we do not want git to track.

### run.py

- In production this is run instead of the code following if \_\_name\_\_ == "\_\_main\_\_": .... in app.py
- This is because we are running the app with uwsgi webserver instead of the flask webserver which is **NOT FOR PRODUCTION**

### Procfile

This is a configuration file that tells heroku to spin up a web dyno that is running the uwsgi webserver with the uwsgi.ini configuration file as input.

- Note: A Heroku dyno is a container that your application runs inside of

- Note: A web dyno is configured to listen on port 80

### runtime.txt

Tells Heroku what language and version to use with you application.

### uwsgi.ini

This is the configuration that tells the uwsgi server how to run.

- http-socket is the port that the server will be listening on

  - It is set to the environment variable called PORT which is equal to 80 since the server is running on a web dyno

- master states that there will be a parent process controlling all children processes.

- die-on-term states that when a uwsgi process is finished running it will be killed and the resources will be released

- module is the location that uwsgi will look to find the app that it is going to run

  - uwsgi is going to find the app object in run.py

## Starting MongoDB

## Testing with Postman

## Heroku Deployment
