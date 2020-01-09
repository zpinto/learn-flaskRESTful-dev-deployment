from flask_restful import Resource, reqparse
from bson import json_util
from bson.objectid import ObjectId
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    fresh_jwt_required,
)

from db import mongo

"""
The following line of code defines a parser for the body of the HTTP requests
that will be made to any of the resources in this file. Once a parser is defined,
arguments can be added to it using the add_argument function.
"""
_todo_parser = reqparse.RequestParser()
_todo_parser.add_argument(
    "name", type=str, required=True, help="This field cannot be left blank!"
)
_todo_parser.add_argument(
    "description", type=str, required=True, help="Every item needs a store_id."
)


class TodoRegister(Resource):
    """
    This resource implements a post method that is used to create new todos that 
    belong to the client making the HTTP request.
    """

    # requires the client making the HTTP request to have a valid access
    # token that is designated as fresh (fresh if token was gained from /login endpoint and not /refresh)
    @fresh_jwt_required
    def post(self):
        # call the parser on the body of the request and store dict of args in data
        data = _todo_parser.parse_args()

        try:
            # insert document into todos collection of mongodb and store object id
            todo_id = mongo.db.todos.insert_one(
                {
                    "name": data["name"],
                    "description": data["description"],
                    "owner_id": get_jwt_identity(),
                }
            ).inserted_id
        except:
            return {"message": "An error occurred creating the todo"}, 500

        try:
            # look for first document in todos collection to have object id of todo_id
            todo = mongo.db.todos.find_one({"_id": ObjectId(todo_id)})
        except:
            return {"message": "An error occurred looking up the todo"}, 500

        # return todo converted to json
        return json_util._json_convert(todo), 201


class Todo(Resource):
    """
    This resource implements a get, put, and delete method that can be used to get,
    update, or delete a specific todo given its object id and that the client making
    the HTTP request own the todo.
    """

    # requires the client making the HTTP request to have a valid access
    @jwt_required
    def get(self, todo_id):
        try:
            # look for first document in todos collection to have object id of todo_id
            todo = mongo.db.todos.find_one({"_id": ObjectId(todo_id)})
        except:
            return {"message": "An error occurred looking up the todo"}, 500

        if not todo:
            return {"message": "Todo not found"}, 404

        # check that current user is the owner of the todo
        if todo["owner_id"] != get_jwt_identity():
            return {"message: you do not have access to this todo"}, 401

        return json_util._json_convert(todo), 200

    # requires the client making the HTTP request to have a valid access
    # token that is designated as fresh (fresh if token was gained from /login endpoint and not /refresh)
    @fresh_jwt_required
    def delete(self, todo_id):
        try:
            # look for first document in todos collection to have object id of todo_id
            todo = mongo.db.todos.find_one({"_id": ObjectId(todo_id)})
        except:
            return {"message": "An error occurred looking up the todo"}, 500

        if not todo:
            return {"message": "Todo not found"}, 404

        # check that current user is the owner of the todo
        if todo["owner_id"] != get_jwt_identity():
            return {"message: you do not have access to this todo"}, 401

        try:
            # deletes first todo in todos collection with object id of todo['_id']
            mongo.db.todos.delete_one({"_id": todo.get("_id")})
        except:
            return {"message": "An error occured while deleting the todo"}, 500

        return {"message": "The todo was deleted"}, 200

    # requires the client making the HTTP request to have a valid access
    # token that is designated as fresh (fresh if token was gained from /login endpoint and not /refresh)
    @fresh_jwt_required
    def put(self, todo_id):
        # call the parser on the body of the request and store dict of args in data
        data = _todo_parser.parse_args()

        try:
            # look for first document in todos collection to have object id of todo_id
            todo = mongo.db.todos.find_one({"_id": ObjectId(todo_id)})
        except:
            return {"message": "An error occurred looking up the todo"}, 500

        if not todo:
            return {"message": "Todo not found"}, 404

        # check that current user is the owner of the todo
        if todo["owner_id"] != get_jwt_identity():
            return {"message: you do not have access to this todo"}, 401

        try:
            # update todo document with object id of todo['_id'] with following data
            mongo.db.todos.update_one(
                {"_id": todo.get("_id")},
                {"$set": {"name": data["name"], "description": data["description"]}},
            )
        except:
            return {"message": "An error occured updating the todo"}, 500

        try:
            # look for first document in todos collection to have object id of todo_id
            todo = mongo.db.todos.find_one({"_id": ObjectId(todo_id)})
        except:
            return {"message": "An error occurred looking up the todo"}, 500

        # return todo converted to json
        return json_util._json_convert(todo), 200


class TodoList(Resource):
    """
    This resource implements a get method that will return a list of all todos belonging
    to the logged in user.
    """

    # requires the client making the HTTP request to have a valid access
    @jwt_required
    def get(self):
        try:
            # looks for all todos in todos collection that have the key "owner_id" equal to the logged in user
            todos = mongo.db.todos.find({"owner_id": get_jwt_identity()})
        except:
            return {"message": "An error occurred looking all of this users todos"}, 500

        if todos.count():
            # returns a list of todos converted to json
            return json_util._json_convert(todos), 200
        return {"message": "No todos found for this user"}, 404
