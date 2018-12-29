from flask import Blueprint, jsonify, request, session
from bson import ObjectId
from auth import sign_check, raise_status, es_delete, es_bulk
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
        change_status = request.json.get('change_status')
        recommend_status = request.json.get('recommend_status')
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
        if shelf_status or change_status or check_status or recommend_status:
            if shelf_status == '0' or check_status == '0' or change_status == '0' or recommend_status == '0':
                data_search['$and'] = []
            if shelf_status == '1':
                data_search['shelf_status'] = shelf_status
            elif shelf_status == '0':
                shelf = {'$or': [{'shelf_status': '0'}, {'shelf_status': {'$exists': 0}}]}
                data_search['$and'].append(shelf)
                # data_search['$or'] = [{'shelf_status': '0'}, {'shelf_status': {'$exists': 0}}]
            if check_status == '1':
                data_search['check_status'] = check_status
            elif check_status == '0':
                check = {'$or': [{'check_status': '0'}, {'check_status': {'$exists': 0}}]}
                data_search['$and'].append(check)
                # data_search['$or'] = [{'check_status': '0'}, {'check_status': {'$exists': 0}}]
            if change_status == '1':
                data_search['change_status'] = change_status
            elif change_status == '0':
                change = {'$or': [{'change_status': '0'}, {'change_status': {'$exists': 0}}]}
                data_search['$and'].append(change)
                # data_search['$or'] = [{'change_status': '0'}, {'change_status': {'$exists': 0}}]
            elif change_status == '2':
                data_search['change_status'] = change_status
            elif change_status == '11':
                change = {'$or': [{'change_status': '0'}, {'change_status': {'$exists': 0}}, {'change_status': '1'}]}
                data_search['$and'].append(change)
            elif change_status == '12':
                change = {'$or': [{'change_status': '1'}, {'change_status': '2'}]}
                data_search['$and'].append(change)
            if recommend_status == '1':
                data_search['recommend_status'] = recommend_status
            elif recommend_status == '0':
                recommend = {'$or': [{'recommend_status': '0'}, {'recommend_status': {'$exists': 0}}]}
                data_search['$and'].append(recommend)
        start = int(request.args.get('start', '0'))
        end = int(request.args.get('end', '30'))
        length = end - start
        count_excerpt = db.t_excerpts.find(data_search).count()
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
            excerptObj['shelf_status'] = digest.get('shelf_status', '0')
            excerptObj['check_status'] = digest.get('check_status', '0')
            excerptObj['change_status'] = digest.get('change_status', '0')
            excerptObj['recommend_status'] = digest.get('recommend_status', '0')
            dataObj.append(excerptObj)
        returnObj['data'] = dataObj
        returnObj['count'] = count_excerpt
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
        excerpt_list = request.json.get('excerpt_list')
        for data_book in excerpt_list:
            excerpt_id = data_book.get('excerpt_id')
            ck_exp_chp_id = data_book.get('ck_exp_chp_id')
            ck_exp_chp_title = data_book.get('ck_exp_chp_title')
            ck_exp_text = data_book.get('ck_exp_text')
            ck_is_hot_exp = data_book.get('ck_is_hot_exp')
            # if not ck_is_hot_exp and not ck_exp_text and not ck_exp_chp_title and not ck_exp_chp_id:
            #     info = '没有修改信息'
            #     return raise_status(400, info)
            db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$set': {
                'ck_exp_chp_id': ck_exp_chp_id,
                'ck_exp_chp_title': ck_exp_chp_title,
                'ck_exp_text': ck_exp_text,
                'ck_is_hot_exp': ck_is_hot_exp,
                'change_status': '1'
            }})
            operation = {session['id']: [session['username'], 'update', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]}
            db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$push': {'operation': operation}})
            summary = db.t_excerpts.find_one({'_id': ObjectId(excerpt_id)})
            book_id = summary['bookid']
            data_count = db.t_books.find_one({'_id': ObjectId(book_id)})
            if data_count.get('digest_ck'):
                digest_ck = data_count['digest_ck']
                digest_ck[0] = digest_ck[0] - 1
            else:
                digest_count = db.t_excerpts.count({'bookid': book_id})
                ck_count = db.t_excerpts.count({'bookid': book_id, 'change_status': '1'})
                digest_ck = [ck_count, digest_count]
            db.t_books.update({'_id': ObjectId(book_id)}, {'$set': {'digest_ck': digest_ck}})
            # data['ck_exp_chp_id'] = ck_exp_chp_id
            # data['ck_exp_chp_title'] = ck_exp_chp_title
            # data['ck_exp_text'] = ck_exp_text
            # data['ck_is_hot_exp'] = ck_is_hot_exp
            # data['change_status'] = '1'
            # operation = data.get('operation', [])
            # operation.append({session['id']: [session['username'],'update',\
            #                                   datetime.now().strftime('%Y-%m-%d %H:%M:%S')]})
            # data['operation'] = operation
            # db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$set': data})
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
        bookid = request.json.get('bookid')
        # book_name = request.json.get('book_name')
        exp_text = request.json.get('exp_text')
        # exp_chp_id = request.json.get('exp_chp_id')
        # exp_chp_title = request.json.get('exp_chp_title')
        is_hot_exp = request.json.get('is_hot_exp')
        if not bookid or not exp_text or not is_hot_exp:
            info = '有未填信息'
            return raise_status(400, info)
        data = db.t_books.find_one({'_id': ObjectId(bookid)})
        book_name = data['book_name']
        operation = {session['id']: [session['username'], 'insert', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]}
        data_insert = []
        for content in exp_text:
            excerpt = {
                'bookid': bookid,
                'book_name': book_name,
                'exp_text': content,
                'exp_chp_id': '',
                'exp_chp_title': '',
                'is_hot_exp': is_hot_exp,
                'operation': [operation],
                'check_status': '0',
                'shelf_status': '0',
                'change_status': '1',
                'recommend_status': '0'
            }
            data_insert.append(excerpt)
        db.t_excerpts.insert_many(data_insert)
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
        key_status = 0
        list = request.json.get('list')
        action = request.args.get('action')
        if action == 'up':
            excerpt_doc = []
            for excerpt_id in list:
                data_excerpt = db.t_excerpts.find_one({'_id': ObjectId(excerpt_id)})
                if data_excerpt.get('shelf_status') == '1':
                    info = '有书摘已上架'
                    key_status = 1
                    continue
                data_check = db.t_books.find_one({'_id': ObjectId(data_excerpt['bookid'])})
                if data_check.get('shelf_status') == '1':
                    operation = {session['id']: [session['username'], 'up', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]}
                    db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$push': {'operation': operation}})
                    db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$set': {'shelf_status': '1'}})
                    del data_excerpt['_id']
                    doc = {'index': {'_index': 't_books', '_type': 'digest', '_id': excerpt_id}}
                    excerpt_doc.append(doc)
                    excerpt_doc.append(data_excerpt)
                else:
                    info = '有书籍未上架'
                    key_status = 1
            if key_status == 0:
                es_bulk('t_excerpts', excerpt_doc)
            elif excerpt_doc == []:
                info = '书摘均已上架或有书籍未上架'
                return raise_status(400, info)
        elif action == 'down':
            for excerpt_id in list:
                operation = {session['id']: [session['username'], 'down', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]}
                db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$push': {'operation': operation}})
                db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$set': {'shelf_status': '0',\
                                                                              'check_status': '0', 'change_status': '0'}})
                try:
                    es_delete('t_excerpts', excerpt_id)
                except Exception as e:
                    info = '有书摘存在异常，请重新点击查询'
                    key_status = 1
        elif action == 'pass':
            for excerpt_id in list:
                operation = {session['id']: [session['username'], 'pass', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]}
                data = db.t_excerpts.find_one({'_id': ObjectId(excerpt_id)})
                # data['exp_chp_id'] = data['ck_exp_chp_id']
                # data['exp_chp_title'] = data['ck_exp_chp_title']
                if data.get('change_status') == '2':
                    db.t_excerpts.remove({'_id': ObjectId(excerpt_id)})
                if data.get('ck_exp_text'):
                    data['exp_text'] = data['ck_exp_text']
                if data.get('ck_is_hot_exp'):
                    data['is_hot_exp'] = data['ck_is_hot_exp']
                data['check_status'] = "1"
                db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$push': {'operation': operation}})
                db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, data)
        elif action == 'refuse':
            for excerpt_id in list:
                operation = {session['id']: [session['username'], 'refuse', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]}
                db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$push': {'operation': operation}})
                db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$set': {'check_status': '0', 'change_status': '0'}})
        elif action == 'recommend':
            for excerpt_id in list:
                data_check = db.t_excerpts.find_one({'_id': ObjectId(excerpt_id)})
                if data_check.get('shelf_status') == '1':
                    operation = {session['id']: [session['username'], 'recommend',\
                                                 datetime.now().strftime('%Y-%m-%d %H:%M:%S')]}
                    db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$push': {'operation': operation}})
                    db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$set': {'recommend_status': '1'}})
                else:
                    info = '有未上架书摘'
                    key_status = 1
        elif action == 'deprecated':
            for excerpt_id in list:
                operation = {session['id']: [session['username'], 'deprecated',\
                                             datetime.now().strftime('%Y-%m-%d %H:%M:%S')]}
                db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$push': {'operation': operation}})
                db.t_excerpts.update({'_id': ObjectId(excerpt_id)}, {'$set': {'recommend_status': '0'}})
        if key_status == 1:
            return raise_status(400, info)
        returnObj['info'] = '操作成功'
        return jsonify(returnObj)
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '- excerpt_operation error as: ', e)
        return raise_status(500, str(e))

# 删除书摘
@digest.route('/excerpt/del', methods=['DELETE'])
@sign_check()
def excerpt_delete():
    from app import db
    returnObj = {}
    try:
        excerpt_list = request.json.get('excerpt_list')
        for excerpt in excerpt_list:
            db.t_excerpts.update({'_id': ObjectId(excerpt)}, {'$set': {'change_status': '2'}})
        returnObj['info'] = '操作成功'
        return jsonify(returnObj)
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '- excerpt_delete error as: ', e)
        return raise_status(500, str(e))
