import os

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from blacklist import BLACKLIST
from resources.user import UserRegister, User, UserLogin, TokenRefresh, UserLogout
from resources.todo import TodoRegister, Todo, TodoList

# create the app instance
app = Flask(__name__)

"""
Below we will add several config variables to apps config python dictionary.
When app is passed to an argument to other constructors and functions, those 
config variables will be read from that dictionary. This occurs when api, jwt,
and mongo are defined by their constructors.
"""

"""
In the line below, we assign a one of two values to "MONGO_URI". We first try
to read the "MONGODB_URI" environment variable from our system. If that does
not exist, the get function will return the MongoDB URI of our local instance.

This is done because when this code is deployed and in production, it will not
be able to talk to our local instance of MongoDB. Instead, it will talk to an
instance in the cloud. This instance's URI will be defined by the environment
variable called "MONGODB_URI" on the system that the application is deployed to.
"""
app.config["MONGO_URI"] = (
    os.environ.get("MONGODB_URI", "mongodb://localhost:27017/todolistapp")
    + "?retryWrites=false"
)
app.config[
    "PROPAGATE_EXCEPTIONS"
] = True  # exceptions are re-raised rather than being handled by app's error handlers
app.config["JWT_BLACKLIST_ENABLED"] = True  # enable blacklist feature
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = [
    "access",
    "refresh",
]  # allow blacklisting for access and refresh tokens
app.config["JWT_SECRET_KEY"] = "secret"  #

# creates an instance of flask-restful api that will be used to add our resources
api = Api(app)

# creates an instance of jwt manager that will handle authentication for the application
jwt = JWTManager(app)


# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    # Here we blacklist particular JWTs that have been created in the past.
    return decrypted_token["jti"] in BLACKLIST


# The following callbacks are used for customizing jwt response/error messages for certain situations.
@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return (
        jsonify(
            {"message": "Signature verification failed.", "error": "invalid_token"}
        ),
        401,
    )


@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify(
            {
                "description": "Request does not contain an access token.",
                "error": "authorization_required",
            }
        ),
        401,
    )


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return (
        jsonify(
            {"description": "The token is not fresh.", "error": "fresh_token_required"}
        ),
        401,
    )


@jwt.revoked_token_loader
def revoked_token_callback():
    return (
        jsonify(
            {"description": "The token has been revoked.", "error": "token_revoked"}
        ),
        401,
    )


"""
This is where all of our applications resources will be added to the API
when the add_resource function is called, we pass the resource class and
the name of the endpoint that a caller can use to call all of the HTTP methods
defined in those resource classes.
"""
api.add_resource(TodoRegister, "/createtodo")
api.add_resource(Todo, "/todo/<string:todo_id>")
api.add_resource(TodoList, "/todolist")
api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<string:username>")
api.add_resource(UserLogin, "/login")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(UserLogout, "/logout")


"""
The code below is only run when we run the flask dev server locally.
This is because the __name__ variable is set to "__main__" when we run
the app.py file with the python interpretor. In production, we use a 
uwsgi webserver, so __name__ is not equal to "__main__".
"""
if __name__ == "__main__":
    from db import mongo

    mongo.init_app(app)
    app.run(port=5000, debug=True)
