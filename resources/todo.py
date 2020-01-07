from flask_restful import Resource, reqparse
from bson import json_util
from bson.objectid import ObjectId
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    fresh_jwt_required,
)

from db import mongo

_todo_parser = reqparse.RequestParser()
_todo_parser.add_argument(
    "name", type=str, required=True, help="This field cannot be left blank!"
)
_todo_parser.add_argument(
    "description", type=str, required=True, help="Every item needs a store_id."
)


class TodoRegister(Resource):
    @fresh_jwt_required
    def post(self):
        data = _todo_parser.parse_args()

        try:
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
            todo = mongo.db.todos.find_one({"_id": ObjectId(todo_id)})
        except:
            return {"message": "An error occurred looking up the todo"}, 500

        return json_util._json_convert(todo), 201


class Todo(Resource):
    @jwt_required
    def get(self, todo_id):
        try:
            todo = mongo.db.todos.find_one({"_id": ObjectId(todo_id)})
        except:
            return {"message": "An error occurred looking up the todo"}, 500

        if not todo:
            return {"message": "Todo not found"}, 404

        if todo["owner_id"] != get_jwt_identity():
            return {"message: you do not have access to this todo"}, 401

        return json_util._json_convert(todo), 200

    @fresh_jwt_required
    def delete(self, todo_id):
        try:
            todo = mongo.db.todos.find_one({"_id": ObjectId(todo_id)})
        except:
            return {"message": "An error occurred looking up the todo"}, 500

        if not todo:
            return {"message": "Todo not found"}, 404

        if todo["owner_id"] != get_jwt_identity():
            return {"message: you do not have access to this todo"}, 401

        try:
            mongo.db.todos.delete_one({"_id": todo.get("_id")})
        except:
            return {"message": "An error occured while deleting the todo"}, 500

        return {"message": "The todo was deleted"}, 200

    @fresh_jwt_required
    def put(self, todo_id):
        data = _todo_parser.parse_args()

        try:
            todo = mongo.db.todos.find_one({"_id": ObjectId(todo_id)})
        except:
            return {"message": "An error occurred looking up the todo"}, 500

        try:
            todo = mongo.db.todos.find_one({"_id": ObjectId(todo_id)})
        except:
            return {"message": "An error occurred looking up the todo"}, 500

        if not todo:
            return {"message": "Todo not found"}, 404

        if todo["owner_id"] != get_jwt_identity():
            return {"message: you do not have access to this todo"}, 401

        try:
            mongo.db.todos.update_one(
                {"_id": todo.get("_id")},
                {"$set": {"name": data["name"], "description": data["description"]}},
            )
        except:
            return {"message": "An error occured updating the todo"}, 500

        try:
            todo = mongo.db.todos.find_one({"_id": ObjectId(todo_id)})
        except:
            return {"message": "An error occurred looking up the todo"}, 500

        return json_util._json_convert(todo), 200


class TodoList(Resource):
    @jwt_required
    def get(self):
        try:
            todos = mongo.db.todos.find({"owner_id": get_jwt_identity()})
        except:
            return {"message": "An error occurred looking all of this users todos"}, 500

        if todos.count():
            return json_util._json_convert(todos), 200
        return {"message": "No todos found for this user"}, 404
