from flask import Blueprint, jsonify, request, session
from bson import ObjectId
from auth import sign_check

book = Blueprint('excerpt', __name__)

# 书籍查询
@book.route('/book/search', methods=['POST'])
@sign_check()
def book_search():
    from app import db
    returnObj = {}
    try:
        book_name = request.json.get('book_name')
        author_list = request.json.get('author_list')
        tags = request.json.get('tags')
        score = request.json.get('score')
        summary = request.json.get('summary')
        category = request.json.get('category')
        catalog_info = request.json.get('catalog_info')
        publish_info = request.json.get('publish_info')
        shelf_status = request.json.get('shelf_status')
        check_status = request.json.get('check_status')
        data_search = {}
        if publish_info:
            publish_date = publish_info.get('publish_date')
            ISBN = publish_info.get('ISBN')
            binding = publish_info.get('binding')
            price = publish_info.get('price')
            pages = publish_info.get('pages')
            words = publish_info.get('words')
            publisher = publish_info.get('publisher')
            if publish_date:
                data_search['publish_info.publish_date'] = {'$regex': publish_date}
            if ISBN:
                data_search['publish_info.ISBN'] = {'$regex': ISBN}
            if binding:
                data_search['publish_info.binding'] = {'$regex': binding}
            if price:
                data_search['publish_info.price'] = {'$regex': price}
            if pages:
                data_search['publish_info.pages'] = {'$regex': pages}
            if words:
                data_search['publish_info.words'] = {'$regex': words}
            if publisher:
                data_search['publish_info.publisher'] = {'$regex': publisher}
        if book_name:
            data_search['book_name'] = {'$regex': book_name}
        if author_list:
            data_search['author_list'] = {'$regex': author_list}
        if tags:
            data_search['tags'] = {'$regex': tags}
        if score:
            data_search['score'] = {'$regex': score}
        if summary:
            data_search['summary'] = {'$regex': summary}
        if category:
            data_search['category'] = {'$regex': category}
        if catalog_info:
            data_search['catalog_info'] = {'$regex': catalog_info}
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
        books = db.t_books.find(data_search).limit(length).skip(start)
        dataObj = {}
        data_list = []
        for data in books:
            dataObj['book_id'] = str(data['_id'])
            dataObj['book_name'] = data['book_name']
            dataObj['author_list'] = data['author_list']
            dataObj['category'] = data['category']
            dataObj['catalog_info'] = data['catalog_info']
            dataObj['tags'] = data['tags']
            dataObj['summary'] = data['summary']
            dataObj['cover_thumbnail'] = data['cover_thumbnail']
            dataObj['score'] = data['score']
            dataObj['publish_info'] = data['publish_info']
            dataObj['ck_book_name'] = data.get('ck_book_name', data['book_name'])
            dataObj['ck_author_list'] = data.get('ck_author_list', data['author_list'])
            dataObj['ck_category'] = data.get('ck_category', data['category'])
            dataObj['ck_catalog_info'] = data.get('ck_catalog_info', data['catalog_info'])
            dataObj['ck_tags'] = data.get('ck_tags', data['tags'])
            dataObj['ck_summary'] = data.get('ck_summary', data['summary'])
            dataObj['ck_cover_thumbnail'] = data.get('ck_cover_thumbnail', data['cover_thumbnail'])
            dataObj['ck_score'] = data.get('ck_score', data['score'])
            dataObj['ck_publish_info'] = data.get('ck_publish_info', data['publish_info'])
            data_list.append(dataObj)
        returnObj['data'] = data_list
        returnObj['info'] = {'status': '200', 'result': '查询成功'}
    except Exception as e:
        print('book_search error as: ', e)
        returnObj['info'] = {'status': '500', 'result': '后台异常'}
    finally:
        return jsonify(returnObj)

# 书籍修改
@book.route('/book/update', methods=['POST'])
@sign_check()
def book_update():
    from app import db
    returnObj = {}
    try:
        book_id = request.json.get('book_id')
        ck_book_name = request.json.get('ck_book_name')
        ck_author_list = request.json.get('ck_author_list')
        ck_category = request.json.get('ck_category')
        ck_catalog_info = request.json.get('ck_catalog_info')
        ck_tags = request.json.get('ck_tags')
        ck_summary = request.json.get('ck_summary')
        ck_cover_thumbnail = request.json.get('ck_cover_thumbnail')
        ck_score = request.json.get('ck_score')
        ck_publish_info = request.json.get('ck_publish_info')
        data_update = {}
        if ck_book_name:
            data_update['ck_book_name'] = ck_book_name
        if ck_author_list:
            data_update['ck_author_list'] = ck_author_list
        if ck_category:
            data_update['ck_category'] = ck_category
        if ck_catalog_info:
            data_update['ck_catalog_info'] = ck_catalog_info
        if ck_tags:
            data_update['ck_tags'] = ck_tags
        if ck_summary:
            data_update['ck_summary'] = ck_summary
        if ck_cover_thumbnail:
            data_update['ck_cover_thumbnail'] = ck_cover_thumbnail
        if ck_score:
            data_update['ck_score'] = ck_score
        if ck_publish_info:
            data_update['ck_publish_info'] = ck_publish_info
        operation = {session['id']: [session['username'], 'update']}
        db.t_books.update({'_id': ObjectId(book_id)}, {'$push': {'operation': operation}})
        db.t_books.update({'_id': ObjectId(book_id)}, {'$set': data_update})
        returnObj['info'] = {'status': '200', 'result': '修改成功'}
    except Exception as e:
        print('book_update error as: ', e)
        returnObj['info'] = {'status': '500', 'result': '后台异常'}
    finally:
        return jsonify(returnObj)

# 书籍录入
@book.route('/book/insert', methods=['PUT'])
@sign_check()
def book_insert():
    from app import db
    returnObj = {}
    try:
        # 13个字段
        tags = request.json.get('tags')
        score = request.json.get('score')
        subtitle = request.json.get('sbutitle')
        author_list = request.json.get('author_list')
        all_version = request.json.get('all_version')
        summary = request.json.get('summary')
        original_name = request.json.get('original_name')
        category = request.json.get('category')
        cover_thumbnail = request.json.get('cover_thumbnail')
        publish_info = request.json.get('publish_info')
        catalog_info = request.json.get('catalog_info')
        series = request.json.get('series')
        book_name = request.json.get('book_name')
        dataObj = {}
        dataObj['book_name'] = book_name
        dataObj['tags'] = tags
        dataObj['score'] = score
        dataObj['subtitle'] = subtitle
        dataObj['author_list'] = author_list
        dataObj['all_version'] = all_version
        dataObj['summary'] = summary
        dataObj['original_name'] = original_name
        dataObj['category'] = category
        dataObj['cover_thumbnail'] = cover_thumbnail
        dataObj['publish_info'] = publish_info
        dataObj['catalog_info'] = catalog_info
        dataObj['series'] = series
        db.t_books.insert(dataObj)
        returnObj['info'] = {'status': '200', 'result': '录入成功'}
    except Exception as e:
        print('book_insert error as: ', e)
        returnObj['info'] = {'status': '500', 'result': '后台异常'}
    finally:
        return jsonify(returnObj)

# 操作书籍
@book.route('/book/operation', methods=['POST'])
@sign_check()
def book_operation():
    from app import db
    returnObj = {}
    try:
        list = request.json.get('data')
        action = request.args.get('action')
        if action == 'up':
            for book_id in list:
                operation = {session['id']: [session['username'], 'up']}
                db.t_books.update({'_id': ObjectId(book_id)}, {'$push': {'operation': operation}})
                db.t_books.update({'_id': ObjectId(book_id)}, {'$set': {'shelf_status': '1'}})
        elif action == 'down':
            for book_id in list:
                operation = {session['id']: [session['username'], 'down']}
                db.t_books.update({'_id': ObjectId(book_id)}, {'$push': {'operation': operation}})
                db.t_books.update({'_id': ObjectId(book_id)}, {'$set': {'shelf_status': '0'}})
        elif action == 'pass':
            for book_id in list:
                operation = {session['id']: [session['username'], 'pass']}
                db.t_books.update({'_id': ObjectId(book_id)}, {'$push': {'operation': operation}})
                db.t_books.update({'_id': ObjectId(book_id)}, {'$set': {'check_status': '1'}})
        elif action == 'refuse':
            for book_id in list:
                operation = {session['id']: [session['username'], 'refuse']}
                db.t_books.update({'_id': ObjectId(book_id)}, {'$push': {'operation': operation}})
                db.t_books.update({'_id': ObjectId(book_id)}, {'$set': {'check_status': '0'}})
        returnObj['info'] = {'status': '200', 'result': '操作成功'}
    except Exception as e:
        print('book_operation error as: ', e)
        returnObj['info'] = {'status': '500', 'result': '后台异常'}
    finally:
        return jsonify(returnObj)
