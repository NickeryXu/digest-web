from flask import session, jsonify
from functools import wraps

def sign_check():
    def sign_decorator(f):
        @wraps(f)
        def sign_function(*args, **kwargs):
            try:
                returnObj = {}
                if 'username' not in session:
                    print("can't find username in session")
                    returnObj['data'] = {}
                    returnObj['info'] = {"result": "400", "info": "请登录后进行操作"}
                    return jsonify(returnObj)
                print('session check success and go on!')
            except Exception as e:
                print("sign_check's error:", e)
                returnObj['data'] = {}
                returnObj['info'] = {"result": "500", "info": "check后台异常"}
                return jsonify(returnObj)
            finally:
                pass
            return f(*args, **kwargs)
        return sign_function
    return sign_decorator
