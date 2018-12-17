from flask import Flask
from flask_cors import *
from datetime import timedelta
import pymongo
import config

app = Flask('digest')
app.config.from_object(config)
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hour=2)
CORS(app, supports_credentials=True)

def register_blueprints():
    from applications.user import user
    from applications.excerpt import digest
    from applications.book import book
    for blueprints in (user, digest, book):
        app.register_blueprint(blueprints)

register_blueprints()

client = pymongo.MongoClient(app.config['MONGODB_HOST'], app.config['MONGODB_PORT'])
db = client[app.config['DATABASE']]
db.authenticate(app.config['USERNAME'], app.config['PASSWORD'])
