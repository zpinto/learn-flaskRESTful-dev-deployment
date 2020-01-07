from app import app
from db import mongo

mongo.init_app(app)
