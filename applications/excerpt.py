from flask import Blueprint, jsonify, request, session
from bson import ObjectId
from auth import sign_check, raise_status
from datetime import datetime

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
        # 查询均采用模糊查询
        if book_name:
            data_search['book_name'] = {'$regex': book_name}
        if exp_text:
            data_search['exp_text'] = {'$regex': exp_text}
        if exp_chp_id:
            data_search['exp_chp_id'] = {'$regex': exp_chp_id}
        if exp_chp_title:
            data_search['exp_chp_title'] = {'$regex': exp_chp_title}
        if is_hot_exp:
            data_search['is_hot_exp'] = {'$regex': is_hot_exp}
        if shelf_status == '1':
            data_search['shelf_status'] = shelf_status
        elif shelf_status == '0':
            data_search['shelf_status'] = {'$or': [{'shelf_status': '0'}, {'shelf_status': {'$exists': 0}}]}
        if check_status == '1':
            data_search['check_status'] = check_status
        elif check_status == '0':
            data_search['check_status'] = {'$or': [{'check_status': '0'}, {'check_status': {'$exists': 0}}]}
        start = int(request.args.get('start', '0'))
        end = int(request.args.get('end', '15'))
        length = end - start
        data = db.t_excerpts.find(data_search).limit(length).skip(start)
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
        returnObj['info'] = '查询成功'
        return jsonify(returnObj)
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '- excerpt_search error as: ', e)
        return raise_status(500, str(e))

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
        returnObj['info'] = '修改成功'
        return jsonify(returnObj)
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '- excerpt_update error as: ', e)
        return raise_status(500, str(e))

# 书摘录入
@digest.route('/excerpt/insert', methods=['POST'])
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
        if not book_id or not book_name or not exp_chp_title or not exp_chp_id or not exp_text or not is_hot_exp:
            info = '有未填信息'
            return raise_status(400, info)
        db.t_excerpts.insert({
            'book_id': book_id,
            'book_name': book_name,
            'exp_text': exp_text,
            'exp_chp_id': exp_chp_id,
            'exp_chp_title': exp_chp_title,
            'is_hot_exp': is_hot_exp
        })
        returnObj['info'] = '录入成功'
        return jsonify(returnObj)
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '- excerpt_insert error as: ', e)
        return raise_status(500, str(e))

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
        returnObj['info'] = '操作成功'
        return jsonify(returnObj)
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '- excerpt_operation error as: ', e)
        return raise_status(500, str(e))
