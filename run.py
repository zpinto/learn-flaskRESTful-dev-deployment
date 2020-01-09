from app import app
from db import mongo

"""
This is file is run in production by the uwsgi web server.
uwsgi imports app from here instead of executing app.run(...) in app.py.

This is setup in the uwsgi configuration file called uwsgi.ini where the 
module is set to run:app. "run" means run.py and "app" is refering to the
app object imported in run.py.
"""

mongo.init_app(app)
