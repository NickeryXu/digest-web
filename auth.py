from flask import session, make_response
from elasticsearch import Elasticsearch
from functools import wraps
from datetime import datetime

def sign_check():
    def sign_decorator(f):
        @wraps(f)
        def sign_function(*args, **kwargs):
            try:
                if 'username' not in session:
                    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "- can't find username in session")
                    return raise_status(400, "请登录后进行操作")
                # print('session check success and go on!')
            except Exception as e:
                print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "- sign_check's error:", e)
                return raise_status(500, "sign_check后台异常")
            return f(*args, **kwargs)
        return sign_function
    return sign_decorator

def raise_status(status, result):
    resp = make_response()
    resp.status_code = status
    resp.headers['content-type'] = 'plain/text'
    resp.response = result
    return resp

def es_insert(index, eid, data):
    es = Elasticsearch(['47.110.77.43:9200'])
    es.index(index=index, doc_type='digest', id=eid, body=data)

def es_delete(index, eid):
    es = Elasticsearch(['47.110.77.43:9200'])
    es.delete(index=index, doc_type='digest', id=eid)
