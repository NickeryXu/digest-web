from flask import Blueprint, jsonify, request, session
from bson import ObjectId
from auth import sign_check

digest = Blueprint('digest', __name__)

# 书摘查询
@digest.route('/excerpt/search', methods=['POST'])
@sign_check()
def excerpt_search():
    from app import db
    returnObj = {}
    try:
        data_search = {}
        book_name = request.json.get('book_name')
        exp_text = request.json.get('exp_text')
        exp_chp_id = request.json.get('exp_chp_id')
        exp_chp_title = request.json.get('exp_chp_title')
        is_hot_exp = request.json.get('is_hot_exp')
        shelf_status = request.json.get('shelf_status')
        check_status = request.json.get('check_status')
        if book_name:
            data_search['book_name'] = book_name
        if exp_text:
            data_search['exp_text'] = exp_text
        if exp_chp_id:
            data_search['exp_chp_id'] = exp_chp_id
        if exp_chp_title:
            data_search['exp_chp_title'] = exp_chp_title
        if is_hot_exp:
            data_search['is_hot_exp'] = is_hot_exp
        if shelf_status:
            data_search['shelf_status'] = shelf_status
        if check_status:
            data_search['check_status'] = check_status
        if not data_search:
            data = db.t_excerpts.find()
        else:
            data = db.t_excerpts.find({data_search})
        dataObj = []
        # 查询出的文档可能没有ck字段，即没有修改内容，所以采用get方法，修改内容取原始内容
        for digest in data:
            excerptObj = {}
            excerptObj['excerpt_id'] = str(digest['_id'])
            excerptObj['exp_chp_id'] = digest['exp_chp_id']
            excerptObj['exp_chp_title'] = digest['exp_chp_title']
            excerptObj['exp_text'] = digest['exp_text']
            excerptObj['book_name'] = digest['book_name']
            excerptObj['is_hot_exp'] = digest['is_hot_exp']
            excerptObj['ck_exp_chp_id'] = digest.get('ck_exp_chp_id', digest['exp_chp_id'])
            excerptObj['ck_exp_chp_title'] = digest.get('ck_exp_chp_title', digest['exp_chp_title'])
            excerptObj['ck_exp_text'] = digest.get('ck_exp_text', digest['exp_text'])
            excerptObj['ck_is_hot_exp'] = digest.get('ck_is_hot_exp', digest['is_hot_exp'])
            dataObj.append(excerptObj)
        returnObj['data'] = dataObj
        returnObj['info'] = {'status': '200', 'result': '查询成功'}
    except Exception as e:
        print('excerpt_search error as: ', e)
        returnObj['info'] = {'status': '500', 'result': '后台异常'}
    finally:
        return jsonify(returnObj)

# 书摘修改
@digest.route('/excerpt/update', methods=['POST'])
@sign_check()
def excerpt_update():
    from app import db
    returnObj = {}
    try:
        excerpt_id = request.json.get('excerpt_id')
        ck_exp_chp_id = request.json.get('ck_exp_chp_id')
        ck_exp_chp_title = request.json.get('ck_exp_chp_title')
        ck_exp_text = request.json.get('ck_exp_text')
        ck_is_hot_exp = request.json.get('ck_is_hot_exp')
        data = db.t_excerpts.find_one({'_id': ObjectId(excerpt_id)})
        data['ck_exp_chp_id'] = ck_exp_chp_id
        data['ck_exp_chp_title'] = ck_exp_chp_title
        data['ck_exp_text'] = ck_exp_text
        data['ck_is_hot_exp'] = ck_is_hot_exp
        operation = data.get('operation', [])
        operation.append({session['id']: [session['username'], 'update']})
        data['operation'] = operation
        db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$set': data})
        returnObj['info'] = {'status': '200', 'result': '修改成功'}
    except Exception as e:
        print('excerpt_update error as: ', e)
        returnObj['info'] = {'status': '500', 'result': '后台异常'}
    finally:
        return jsonify(returnObj)

# 书摘录入
@digest.route('/excerpt/insert', methods=['PUT'])
@sign_check()
def excerpt_insert():
    from app import db
    returnObj = {}
    try:
        book_id = request.json.get('book_id')
        book_name = request.json.get('book_name')
        exp_text = request.json.get('exp_text')
        exp_chp_id = request.json.get('exp_chp_id')
        exp_chp_title = request.json.get('exp_chp_title')
        is_hot_exp = request.json.get('is_hot_exp')
        db.t_excerpts.insert({
            'book_id': book_id,
            'book_name': book_name,
            'exp_text': exp_text,
            'exp_chp_id': exp_chp_id,
            'exp_chp_title': exp_chp_title,
            'is_hot_exp': is_hot_exp
        })
        returnObj['info'] = {'status': '200', 'result': '录入成功'}
    except Exception as e:
        print('excerpt_insert error as: ', e)
        returnObj['info'] = {'status': '500', 'result': '后台异常'}
    finally:
        return jsonify(returnObj)

# 操作书摘
@digest.route('/excerpt/operation', methods=['POST'])
@sign_check()
def excerpt_operation():
    from app import db
    returnObj = {}
    try:
        list = request.json.get('data')
        action = request.args.get('action')
        if action == 'up':
            for excerpt_id in list:
                operation = {session['id']: [session['username'], 'up']}
                db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$push': {'operation': operation}})
                db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$set': {'shelf_status': '1'}})
        elif action == 'down':
            for excerpt_id in list:
                operation = {session['id']: [session['username'], 'down']}
                db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$push': {'operation': operation}})
                db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$set': {'shelf_status': '0'}})
        elif action == 'pass':
            for excerpt_id in list:
                operation = {session['id']: [session['username'], 'pass']}
                db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$push': {'operation': operation}})
                db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$set': {'check_status': '1'}})
        elif action == 'refuse':
            for excerpt_id in list:
                operation = {session['id']: [session['username'], 'refuse']}
                db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$push': {'operation': operation}})
                db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$set': {'check_status': '0'}})
        elif action == 'recommend':
            for excerpt_id in list:
                operation = {session['id']: [session['username'], 'recommend']}
                db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$push': {'operation': operation}})
                db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$set': {'recommend_status': '1'}})
        elif action == 'deprecated':
            for excerpt_id in list:
                operation = {session['id']: [session['username'], 'deprecated']}
                db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$push': {'operation': operation}})
                db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$set': {'recommend_status': '0'}})
        returnObj['info'] = {'status': '200', 'result': '操作成功'}
    except Exception as e:
        print('excerpt_operation error as: ', e)
        returnObj['info'] = {'status': '500', 'result': '后台异常'}
    finally:
        return jsonify(returnObj)
