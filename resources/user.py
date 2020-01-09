from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from bson import json_util
from bson.objectid import ObjectId
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
)
from blacklist import BLACKLIST

from db import mongo

"""
The following line of code defines a parser for the body of the HTTP requests
that will be made to any of the resources in this file. Once a parser is defined,
arguments can be added to it using the add_argument function.
"""
_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
    "username", type=str, required=True, help="This field cannot be blank."
)
_user_parser.add_argument(
    "password", type=str, required=True, help="This field cannot be blank."
)


class UserRegister(Resource):
    """
    This resource implements a post method that allows the client to create a user with a 
    unique username and a password.
    """

    def post(self):
        # call the parser on the body of the request and store dict of args in data
        data = _user_parser.parse_args()

        # search to make sure that another user with the same username does not exist
        try:
            # look for first document in users collection to have a username data['username']
            user = mongo.db.users.find_one({"username": data["username"]})
        except:
            return {"message": "An error occurred looking up the user"}, 500

        if user:
            return {"message": "A user with that username already exists"}, 400

        try:
            # insert document into users collection
            mongo.db.users.insert_one(
                {"username": data["username"], "password": data["password"]}
            )

            return {"message": "User created successfully."}, 201
        except:
            return {"message": "An error occurred creating the user"}, 500


class User(Resource):
    """
    This resource implements a get and delete method that allow the client to get all of the data about a user 
    or delete a user given the username.

    This resource can be useful when testing our Flask app. We may not want to expose it to public users, but 
    for the sake of demonstration in this course, it can be useful when we are manipulating data regarding the 
    users.
    """

    @classmethod
    def get(cls, username):
        try:
            # look for first document in users collection to have a username equal to ata['username']
            user = mongo.db.users.find_one({"username": username})
        except:
            return {"message": "An error occurred looking up the user"}, 500

        if user:
            # return user converted to json
            return json_util._json_convert(user), 200
        return {"message": "user not found"}, 404

    @classmethod
    def delete(cls, username):
        try:
            # look for first document in users collection to have a username data['username']
            user = mongo.db.users.find_one({"username": username})
        except:
            return {"message": "An error occurred trying to look up this user"}, 500

        if user:
            try:
                # delete first document in users collection to have a username equal to  username
                mongo.db.users.delete_one({"username": username})
            except:
                return {"message": "An error occurred trying to delete this user"}, 500
            return {"message": "User was deleted"}, 200
        return {"message": "User not found"}, 404


class UserLogin(Resource):
    """
    This resource implements a post method that allows a client to login to an existing 
    account and receive a access_token and refresh_token.
    """

    def post(self):
        # call the parser on the body of the request and store dict of args in data
        data = _user_parser.parse_args()

        try:
            # look for first document in users collection to have a username data['username']
            user = mongo.db.users.find_one({"username": data["username"]})
        except:
            return {"message": "An error occurred trying to look up this user"}, 500

        # safe_str_cmp checks to make passwords match
        if user and safe_str_cmp(user["password"], data["password"]):
            # create new fresh access token that binds to the identity of the user (users.get("_id"))
            # identity=str(user.get("_id")) is what makes get_jwt_identity() in todo.py return the object id of the user
            access_token = create_access_token(
                identity=str(user.get("_id")), fresh=True
            )
            # create new refresh token that binds to the identity of the user (users.get("_id"))
            refresh_token = create_refresh_token(str(user.get("_id")))
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        return {"message": "Invalid Credentials!"}, 401


class UserLogout(Resource):
    """
    This resource implements a post method that allows the user to log out and end their
    session by adding the session id to the blacklist.
    """

    # requires the client making the HTTP request to have a valid access
    @jwt_required
    def post(self):
        jti = get_raw_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
        BLACKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200


class TokenRefresh(Resource):
    """
    This resource implements a post method that allows the user to refresh their access_token,
    so they can reestablish their session.
    """

    # requires the client making the HTTP request to have a refresh_token they received when they logged in
    @jwt_refresh_token_required
    def post(self):
        """
        Get a new access token without requiring username and password—only the 'refresh token'
        provided in the /login endpoint.

        Note that refreshed access tokens have a `fresh=False`, which means that the user may have not
        given us their username and password for potentially a long time (if the token has been
        refreshed many times over).
        """
        # gets the users identity which is their object id in mongo
        current_user = get_jwt_identity()
        # create a new access token that is not fresh
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
