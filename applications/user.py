from flask import Blueprint, jsonify, request, session
from bson import ObjectId
from auth import sign_check, raise_status
from datetime import datetime

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
        mobile = request.json.get('mobile', '')
        email = request.json.get('email', '')
        remark = request.json.get('remark', '')
        role_list = request.json.get('role_list')
        data_check = db.mg_user.find_one({'username': username})
        if data_check:
            info = '用户名重复'
            return raise_status(400, info)
        else:
            if not username or not password or not role_list:
                info = '有未填信息'
                return raise_status(400, info)
            data = {
                'username': username,
                'password': password,
                'mobile': mobile,
                'email': email,
                'remark': remark,
                'role_list': role_list
            }
            db.mg_user.insert(data)
            returnObj['info'] = '创建成功'
            return jsonify(returnObj)
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '- signup error as:', e)
        return raise_status(500, str(e))

# 角色列表
@user.route('/user/role_list', methods=['GET'])
def role_list():
    list = [
        {'id': '101', 'name': '书摘录入', 'path': '/excerpt/add'},
        {'id': '102', 'name': '书摘校验', 'path': '/excerpt/search'},
        {'id': '103', 'name': '书摘审核', 'path': '/excerpt/check'},
        {'id': '104', 'name': '书摘上架', 'path': '/excerpt/manage'},
        {'id': '105', 'name': '书摘查询', 'path': '/excerpt/query'},
        {'id': '201', 'name': '书籍录入', 'path': '/book/add'},
        {'id': '202', 'name': '书籍校验', 'path': '/book/search'},
        {'id': '203', 'name': '书籍审核', 'path': '/book/check'},
        {'id': '204', 'name': '书籍上架', 'path': '/book/manage'},
        {'id': '205', 'name': '书籍查询', 'path': '/book/query'},
        {'id': '301', 'name': '添加用户', 'path': '/user/manage'},
        {'id': '302', 'name': '个人设置', 'path': '/user/profile'}
    ]
    returnObj = {'data': list}
    return jsonify(returnObj)

# 用户登录
@user.route('/user/login', methods=['POST'])
def login():
    from app import db
    from datetime import datetime
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
            icon_list = {'1': 'home', '2': 'yonghu', '3': 'yonghu'}
            # 数据库中取出该用户权限列表，判断并生成基础菜单和进阶菜单
            for single in role_list:
                key = 0
                for menu in role:
                    if single['id'][0] == menu.get('id'):
                        menu['children'].append(single)
                        key = 1
                if key == 0:
                    menu_id = single['id'][0]
                    menu = {
                        'id': menu_id,
                        'name': collection[menu_id],
                        'icon': icon_list[menu_id],
                        'children': [single]
                    }
                    role.append(menu)
            LoginTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db.mg_user.update({'_id': data_check['_id']}, {'$set': {'RecentLogin': LoginTime}})
            returnObj['data'] = {'username': username, 'role': role}
            returnObj['info'] = '登录成功'
            return jsonify(returnObj)
        else:
            check_username = db.mg_user.find_one({'username': username})
            if check_username:
                info = '密码错误'
                return raise_status(400, info)
            else:
                info = '不存在该用户'
                return raise_status(400, info)
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '- login error as: ', e)
        return raise_status(500, str(e))

# 查询用户菜单
@user.route('/user/profile', methods=['GET'])
@sign_check()
def user_profile():
    from app import db
    try:
        user_id = session['id']
        data = db.mg_user.find_one({'_id': ObjectId(user_id)})
        role_list = data['role_list']
        role = []
        collection = {'1': '书摘模块', '2': '书籍模块', '3': '用户模块'}
        # 数据库中取出该用户权限列表，判断并生成基础菜单和进阶菜单
        for single in role_list:
            key = 0
            for menu in role:
                if single['id'][0] == menu.get('id'):
                    menu['children'].append(single)
                    key = 1
            if key == 0:
                menu_id = single['id'][0]
                menu = {
                    'id': menu_id,
                    'name': collection[menu_id],
                    'children': [single]
                }
                role.append(menu)
        username = session['username']
        email = data.get('email')
        mobile = data.get('mobile')
        remark = data.get('remark')
        returnObj = {
            'data': {
                'username': username,
                'email': email,
                'mobile': mobile,
                'role_list': role,
                'remark': remark
            },
            'info': '查询成功'
        }
        return jsonify(returnObj)
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '- user_profile error as: ', e)
        return raise_status(500, str(e))

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
        password = request.json.get('password')
        data = {}
        # 不一定每个字段都要修改，没有的就忽略掉
        if username:
            if db.mg_user.find_one({'username': username}):
                info = '用户名重复'
                return raise_status(400, info)
            data['username'] = username
        if mobile:
            data['mobile'] = mobile
        if email:
            data['email'] = email
        if remark:
            data['remark'] = remark
        if password:
            data['password'] = password
        db.mg_user.update({'_id': ObjectId(session['id'])}, {'$set': data})
        session['username'] = username
        returnObj['data'] = {'username': username}
        returnObj['info'] = '修改成功'
        return jsonify(returnObj)
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '- change error as: ', e)
        return raise_status(500, str(e))

# 更改当前用户密码(每个人都有权限)
@user.route('/user/password', methods=['POST'])
@sign_check()
def change_password():
    from app import db
    returnObj = {}
    try:
        password = request.json.get('password')
        db.mg_user.update({'_id': ObjectId(session['id'])}, {'$set': {'password': password}})
        returnObj['info'] = '修改成功'
        return jsonify(returnObj)
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '- change_password error as: ', e)
        return raise_status(500, str(e))

# 用户登出
@user.route('/logout', methods=['GET'])
def logout():
    info = {'info': '退出登录'}
    print(session)
    del session['id']
    del session['username']
    return jsonify(info)

# 用户列表
@user.route('/user/manage', methods=['GET'])
@sign_check()
def user_manage():
    from app import db
    returnObj = {}
    try:
        start = int(request.args.get('start', 0))
        end = int(request.args.get('end', 20))
        lmt = end - start
        data_user = db.mg_user.find().limit(lmt).skip(start).sort([('username', 1)])
        count = db.mg_user.find().count()
        returnObj['data'] = []
        for User in data_user:
            username = User['username']
            role_list = User['role_list']
            role = []
            collection = {'1': '书摘模块', '2': '书籍模块', '3': '用户模块'}
            # 数据库中取出该用户权限列表，判断并生成基础菜单和进阶菜单
            for single in role_list:
                key = 0
                for menu in role:
                    if single['id'][0] == menu.get('id'):
                        menu['children'].append(single)
                        key = 1
                if key == 0:
                    menu_id = single['id'][0]
                    menu = {
                        'id': menu_id,
                        'name': collection[menu_id],
                        'children': [single]
                    }
                    role.append(menu)
            email = User['email']
            mobile = User['mobile']
            remark = User['remark']
            uid = str(User['_id'])
            returnObj['data'].append({
                'uid': uid,
                'username': username,
                'mobile': mobile,
                'email': email,
                'role_list': role,
                'remark': remark
            })
            returnObj['count'] = count
        return jsonify(returnObj)
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '- user_manage error as: ', e)
        return raise_status(500, str(e))

# 用户删除
@user.route('/user/del', methods=['POST'])
@sign_check()
def user_delete():
    from app import db
    returnObj = {}
    try:
        user_list = request.json.get('user_list')
        for User in user_list:
            db.mg_user.remove({'username': User})
        returnObj['info'] = '操作成功'
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '- user_delete error as: ', e)
        return raise_status(500, str(e))
