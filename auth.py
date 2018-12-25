from flask import session, make_response
from functools import wraps
from datetime import datetime
from app import es, bucket
import oss2

def sign_check():
    def sign_decorator(f):
        @wraps(f)
        def sign_function(*args, **kwargs):
            try:
                if 'username' not in session:
                    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "- can't find username in session")
                    return raise_status(401, "请登录后进行操作")
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

def es_bulk(index, data):
    es.indices.create(index='t_books', ignore=400)
    es.indices.create(index='t_excerpts', ignore=400)
    es.bulk(index=index, doc_type='digest', body=data, request_timeout=60)

def es_delete(index, eid):
    es.delete(index=index, doc_type='digest', id=eid)

def img_bulk(file, extension):
    filename = 'mz' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.' + extension
    message = 'https://joymiaozhai.oss-cn-hangzhou.aliyuncs.com/t_books_imgs/' + filename
    bucket.put_object('t_books_imgs/' + filename + '.png', file)
    return message
