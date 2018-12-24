from flask import Flask
from flask_cors import *
from elasticsearch import Elasticsearch
from datetime import timedelta
import pymongo
import config

app = Flask('digest')
app.config.from_object(config)
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hour=2)
CORS(app, supports_credentials=True)
es = Elasticsearch(['es-cn-0pp0wdtno00026tz5.public.elasticsearch.aliyuncs.com'], http_auth=('elastic', 'N+8atre&lt'), port=9200)
client = pymongo.MongoReplicaSetClient(app.config['MONGODB_URL'], replicaSet=app.config['SET'])
db = client[app.config['DATABASE']]
db.authenticate(app.config['USERNAME'], app.config['PASSWORD'])
es = Elasticsearch(['es-cn-0pp0wdtno00026tz5.public.elasticsearch.aliyuncs.com'], http_auth=('elastic', 'N+8atre&lt'), port=9200)

def register_blueprints():
    from applications.user import user
    from applications.excerpt import digest
    from applications.book import book
    for blueprints in (user, digest, book):
        app.register_blueprint(blueprints)

register_blueprints()
