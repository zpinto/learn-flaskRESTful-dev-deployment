import os

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from blacklist import BLACKLIST
from resources.user import UserRegister, User, UserLogin, TokenRefresh, UserLogout
from resources.todo import TodoRegister, Todo, TodoList

app = Flask(__name__)
app.config["MONGO_URI"] = (
    os.environ.get("MONGODB_URI", "mongodb://localhost:27017/todolistapp")
    + "?retryWrites=false"
)
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["JWT_BLACKLIST_ENABLED"] = True  # enable blacklist feature
# allow blacklisting for access and refresh tokens
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]
app.config["JWT_SECRET_KEY"] = "secret"
api = Api(app)

jwt = JWTManager(app)


# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    # Here we blacklist particular JWTs that have been created in the past.
    return decrypted_token["jti"] in BLACKLIST


# The following callbacks are used for customizing jwt response/error messages.
# The original ones may not be in a very pretty format (opinionated)
@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401


@jwt.invalid_token_loader
# we have to keep the argument here, since it's passed in by the caller internally
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


api.add_resource(TodoRegister, "/createtodo")
api.add_resource(Todo, "/todo/<string:todo_id>")
api.add_resource(TodoList, "/todolist")
api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<string:username>")
api.add_resource(UserLogin, "/login")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(UserLogout, "/logout")

if __name__ == "__main__":
    from db import mongo

    mongo.init_app(app)
    app.run(port=5000, debug=True)
