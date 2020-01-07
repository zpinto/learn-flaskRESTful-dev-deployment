import traceback

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


_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
    "username", type=str, required=True, help="This field cannot be blank."
)
_user_parser.add_argument(
    "password", type=str, required=True, help="This field cannot be blank."
)


class UserRegister(Resource):
    def post(self):
        data = _user_parser.parse_args()

        # search to make sure that another user with the same username does not exist
        try:
            user = mongo.db.users.find_one({"username": data["username"]})
        except:
            traceback.print_exc()
            return {"message": "An error occured looking up the user"}, 500

        if user:
            return {"message": "A user with that username already exists"}, 400

        try:
            mongo.db.users.insert_one(
                {"username": data["username"], "password": data["password"]}
            )

            return {"message": "User created successfully."}, 201
        except:
            return {"message": "An error occured creating the user"}, 500


class User(Resource):
    """
    This resource can be useful when testing our Flask app. We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful when we are manipulating data regarding the users.
    """

    @classmethod
    def get(cls, username):
        try:
            user = mongo.db.users.find_one({"username": username})
        except:
            return {"message": "An error occured looking up the user"}, 500

        if user:
            return json_util._json_convert(user), 200
        return {"message": "user not found"}, 404

    @classmethod
    def delete(cls, username):
        try:
            user = mongo.db.users.find_one({"username": username})
        except:
            return {"message": "An error occured trying to look up this user"}, 500

        if user:
            try:
                mongo.db.users.delete_one({"username": username})
            except:
                return {"message": "An error occured trying to delete this user"}, 500
            return {"message": "User was deleted"}, 200
        return {"message": "User not found"}, 404


class UserLogin(Resource):
    def post(self):
        data = _user_parser.parse_args()

        user = mongo.db.users.find_one({"username": data["username"]})

        # this is what the `authenticate()` function did in security.py
        if user and safe_str_cmp(user["password"], data["password"]):
            # identity= is what the identity() function did in security.py—now stored in the JWT
            access_token = create_access_token(
                identity=str(user.get("_id")), fresh=True
            )
            refresh_token = create_refresh_token(str(user.get("_id")))
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        return {"message": "Invalid Credentials!"}, 401


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
        BLACKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        """
        Get a new access token without requiring username and password—only the 'refresh token'
        provided in the /login endpoint.

        Note that refreshed access tokens have a `fresh=False`, which means that the user may have not
        given us their username and password for potentially a long time (if the token has been
        refreshed many times over).
        """
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
