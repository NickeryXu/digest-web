from flask import Blueprint, jsonify, request, session
from bson import ObjectId
from auth import sign_check

user = Blueprint('user', __name__)

# 创建用户
@user.route('/user/signup', methods=['POST'])
@sign_check()
def signup():
    from app import db
    returnObj = {}
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        mobile = request.json.get('mobile')
        email = request.json.get('email')
        remark = request.json.get('remark')
        role_list = request.json.get('role_list')
        data_check = db.mg_user.find_one({'username': username})
        if data_check:
            returnObj['info'] = {'status': '400', 'result': '用户名重复'}
        else:
            data = {
                'username': username,
                'password': password,
                'mobile': mobile,
                'email': email,
                'remark': remark,
                'role_list': role_list
            }
            db.mg_user.insert(data)
            returnObj['info'] = {'status': '200', 'result': '创建成功'}
    except Exception as e:
        print('signup error as: ', e)
        returnObj['info'] = {'status': '500', 'result': '后台异常'}
    finally:
        return jsonify(returnObj)

# 角色列表
@user.route('/user/role_list', methods=['GET'])
def role_list():
    list = [
        {'id': '101', 'name': '书摘列表', 'url': ''},
        {'id': '102', 'name': '书摘录入', 'url': ''},
        {'id': '103', 'name': '书摘审核', 'url': ''},
        {'id': '104', 'name': '书摘管理', 'url': ''},
        {'id': '201', 'name': '书籍列表', 'url': ''},
        {'id': '202', 'name': '书籍录入', 'url': ''},
        {'id': '203', 'name': '书籍审核', 'url': ''},
        {'id': '204', 'name': '书籍管理', 'url': ''},
        {'id': '301', 'name': '用户管理', 'url': ''}
    ]
    returnObj = {'role': list}
    return jsonify(returnObj)

# 用户登录
@user.route('/user/login', methods=['POST'])
def login():
    from app import db
    returnObj = {}
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        data_check = db.mg_user.find_one({'username': username, 'password': password})
        if data_check:
            session['username'] = username
            session['id'] = str(data_check['_id'])
            role_list = data_check['role_list']
            role = []
            collection = {'1': '书摘模块', '2': '书籍模块', '3': '用户模块'}
            # 数据库中取出该用户权限列表，判断并生成基础菜单和进阶菜单
            for single in role_list:
                key = 0
                for menu in role:
                    if single['id'][0] == menu.get('id'):
                        menu['advanced_menu'].append(single)
                        key = 1
                if key == 0:
                    menu_id = single['id'][0]
                    menu = {
                        'id': menu_id,
                        'junior_menu': collection[menu_id],
                        'advanced_menu': [single]
                    }
                    role.append(menu)
            returnObj['data'] = {'username': username, 'role': role}
            returnObj['info'] = {'status': '200', 'result': '登录成功'}
        else:
            check_username = db.mg_user.find_one({'username': username})
            if check_username:
                returnObj['info'] = {'status': '400', 'result': '密码错误'}
            else:
                returnObj['info'] = {'status': '400', 'result': '不存在该用户'}
    except Exception as e:
        print('login error as: ', e)
        returnObj['info'] = {'status': '500', 'result': '后台异常'}
    finally:
        return jsonify(returnObj)

# 更改当前用户信息(每个人都有的权限)
@user.route('/user/change', methods=['POST'])
@sign_check()
def change():
    from app import db
    returnObj = {}
    try:
        username = request.json.get('username')
        mobile = request.json.get('mobile')
        email = request.json.get('email')
        remark = request.json.get('remark')
        data = {}
        # 不一定每个字段都要修改，没有的就忽略掉
        if username:
            data['username'] = username
        if mobile:
            data['mobile'] = mobile
        if email:
            data['email'] = email
        if remark:
            data['remark'] = remark
        db.mg_user.update({'_id': ObjectId(session['id'])}, {'$set': data})
        session['username'] = username
        returnObj['data'] = {'username': username}
        returnObj['info'] = {'status': '200', 'result': '修改成功'}
    except Exception as e:
        print('change error as: ', e)
        returnObj['info'] = {'status': '500', 'result': '后台异常'}
    finally:
        return jsonify(returnObj)

# 更改当前用户密码(每个人都有权限)
@user.route('/user/password', methods=['POST'])
@sign_check()
def change_password():
    from app import db
    returnObj = {}
    try:
        password = request.json.get('password')
        db.mg_user.update({'_id': ObjectId(session['id'])}, {'$set': {'password': password}})
        returnObj['info'] = {'status': '200', 'result': '修改成功'}
    except Exception as e:
        print('change_password error as: ', e)
        returnObj['info'] = {'status': '500', 'result': '后台异常'}
    finally:
        return jsonify(returnObj)

# 用户登出
@user.route('/logout', methods=['GET'])
def logout():
    info = {'info': '退出登录'}
    return jsonify(info)
