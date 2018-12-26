from flask import Blueprint, jsonify, request, session
from bson import ObjectId
from auth import sign_check, raise_status, es_delete, es_bulk, img_bulk, redis_zincrby
from datetime import datetime

book = Blueprint('excerpt', __name__,)

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
        change_status = request.json.get('change_status')
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
            data_search['author_list.author_name'] = {'$all': author_list}
        if tags:
            data_search['tags'] = {'$all': tags}
        if score:
            data_search['score'] = {'$regex': score}
        if summary:
            data_search['summary'] = {'$regex': summary}
        if category:
            data_search['category.name'] = {'$all': category}
        if catalog_info:
            data_search['catalog_info'] = {'$all': catalog_info}
        if shelf_status or change_status or check_status:
            if shelf_status == '0' or check_status == '0' or change_status == '0':
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
        start = int(request.args.get('start', '0'))
        end = int(request.args.get('end', '30'))
        length = end - start
        # count_book = 8000000
        count_book = db.t_books.find(data_search).count()
        books = db.t_books.find(data_search).limit(length).skip(start).sort([('score', -1)])
        data_list = []
        for data in books:
            dataObj = {}
            dataObj['book_id'] = str(data['_id'])
            dataObj['book_name'] = data['book_name']
            dataObj['author_list'] = []
            # dataObj['author_list'] = data['author_list']
            for author in data['author_list']:
                dataObj['author_list'].append(author['author_name'])
            dataObj['category'] = []
            for cate in data['category']:
                dataObj['category'].append((cate['name']))
            dataObj['catalog_info'] = data['catalog_info']
            dataObj['tags'] = data['tags']
            dataObj['summary'] = data['summary']
            dataObj['cover_thumbnail'] = data['cover_thumbnail']
            dataObj['score'] = data['score']
            dataObj['publish_info'] = data['publish_info']
            dataObj['ck_book_name'] = data.get('ck_book_name', data['book_name'])
            dataObj['ck_author_list'] = []
            # dataObj['ck_author_list'] = data.get('ck_author_list', data['author_list'])
            for author in data.get('ck_author_list', data['author_list']):
                dataObj['ck_author_list'].append(author['author_name'])
            dataObj['ck_category'] = []
            for ck_cate in data.get('ck_category', data['category']):
                dataObj['ck_category'].append(ck_cate['name'])
            dataObj['ck_catalog_info'] = data.get('ck_catalog_info', data['catalog_info'])
            dataObj['ck_tags'] = data.get('ck_tags', data['tags'])
            dataObj['ck_summary'] = data.get('ck_summary', data['summary'])
            dataObj['ck_cover_thumbnail'] = data.get('ck_cover_thumbnail', data['cover_thumbnail'])
            dataObj['ck_score'] = data.get('ck_score', data['score'])
            dataObj['ck_publish_info'] = data.get('ck_publish_info', data['publish_info'])
            dataObj['check_status'] = data.get('check_status', '0')
            dataObj['shelf_status'] = data.get('shelf_status', '0')
            dataObj['change_status'] = data.get('change_status', '0')
            data_list.append(dataObj)
        returnObj['data'] = data_list
        returnObj['count'] = count_book
        returnObj['info'] = '查询成功'
        return jsonify(returnObj)
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '- book_search error as: ', e)
        return raise_status(500, str(e))

# 书籍修改
@book.route('/book/update', methods=['POST'])
@sign_check()
def book_update():
    from app import db
    returnObj = {}
    try:
        book_list = request.json.get('book_list')
        for data_book in book_list:
            book_id = data_book.get('book_id')
            ck_book_name = data_book.get('ck_book_name')
            author_list = data_book.get('ck_author_list')
            ck_author_list = []
            for author in author_list:
                ck_author_list.append({'id': 1000000, 'author_name': author})
            category_list = data_book.get('ck_category')
            ck_category_list = []
            for category in category_list:
                ck_category_list.append({'id': 100, 'name': category})
            ck_catalog_info = data_book.get('ck_catalog_info')
            ck_tags = data_book.get('ck_tags')
            ck_summary = data_book.get('ck_summary')
            ck_cover_thumbnail = data_book.get('ck_cover_thumbnail')
            ck_score = data_book.get('ck_score')
            ck_publish_info = data_book.get('ck_publish_info')
            # if not ck_book_name and not ck_author_list and not ck_category and not ck_catalog_info and not ck_tags\
            #     and not ck_summary and not ck_cover_thumbnail and not ck_score and not ck_publish_info:
            #     info = '没有修改信息'
            #     return raise_status(400, info)
            data_update = {}
            data_update['ck_book_name'] = ck_book_name
            data_update['ck_author_list'] = ck_author_list
            data_update['ck_category'] = ck_category_list
            data_update['ck_catalog_info'] = ck_catalog_info
            data_update['ck_tags'] = ck_tags
            data_update['ck_summary'] = ck_summary
            data_update['ck_cover_thumbnail'] = ck_cover_thumbnail
            data_update['ck_score'] = ck_score
            data_update['ck_publish_info'] = ck_publish_info
            data_update['change_status'] = '1'
            operation = {session['id']: [session['username'], 'update', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]}
            db.t_books.update({'_id': ObjectId(book_id)}, {'$set': data_update})
            db.t_books.update({'_id': ObjectId(book_id)}, {'$push': {'operation': operation}})
        returnObj['info'] = '修改成功'
        return jsonify(returnObj)
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '- book_update error as: ', e)
        return raise_status(500, str(e))

# 书籍录入
@book.route('/book/insert', methods=['POST'])
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
        category_list = request.json.get('category')
        cover_thumbnail = request.json.get('cover_thumbnail')
        publish_info = request.json.get('publish_info')
        catalog_info = request.json.get('catalog_info')
        series = request.json.get('series')
        book_name = request.json.get('book_name')
        if not tags or not score or not author_list or not summary\
                or not category_list or not publish_info or not catalog_info or not book_name:
            info = '有未填信息'
            return raise_status(400, info)
        dataObj = {}
        dataObj['book_name'] = book_name
        dataObj['tags'] = tags
        dataObj['score'] = score
        if not subtitle:
            subtitle = ''
        dataObj['subtitle'] = subtitle
        list = []
        for author in author_list:
            simple = {'id': 100000, 'author_name': author}
            list.append(simple)
        dataObj['author_list'] = list
        if not all_version:
            all_version = []
        dataObj['all_version'] = all_version
        dataObj['summary'] = summary
        if not original_name:
            original_name = ''
        dataObj['original_name'] = original_name
        list = []
        for category in category_list:
            simple = {'id': 100, 'name': category}
            list.append(simple)
        dataObj['category'] = list
        if not cover_thumbnail:
            cover_thumbnail = "http://wfqqreader-1252317822.image.myqcloud.com/cover/873/21031873/s_21031873.jpg"
        dataObj['cover_thumbnail'] = cover_thumbnail
        dataObj['publish_info'] = publish_info
        dataObj['catalog_info'] = catalog_info
        if not series:
            series = []
        dataObj['series'] = series
        operation = {session['id']: [session['username'], 'insert', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]}
        dataObj['operation'] = [operation]
        dataObj['change_status'] = '1'
        dataObj['shelf_status'] = '0'
        dataObj['check_status'] = '0'
        db.t_books.insert(dataObj)
        returnObj['info'] = '录入成功'
        return jsonify(returnObj)
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '- book_insert error as: ', e)
        return raise_status(500, str(e))

# 操作书籍
@book.route('/book/operation', methods=['POST'])
@sign_check()
def book_operation():
    from app import db
    returnObj = {}
    try:
        list = request.json.get('list')
        action = request.args.get('action')
        key_status = 0
        if action == 'up':
            book_doc = []
            category_list = []
            for book_id in list:
                data_insert = db.t_books.find_one({'_id': ObjectId(book_id)})
                if data_insert.get('shelf_status') == '1':
                    info = '已有上架书籍'
                    key_status = 1
                    continue
                operation = {session['id']: [session['username'], 'up', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]}
                db.t_books.update({'_id': ObjectId(book_id)}, {'$push': {'operation': operation}})
                db.t_books.update({'_id': ObjectId(book_id)}, {'$set': {'shelf_status': '1'}})
                del data_insert['_id']
                doc = {'index': {'_index': 't_books', '_type': 'digest', '_id': book_id}}
                book_doc.append(doc)
                book_doc.append(data_insert)
                for single in data_insert['category']:
                    category_list.append(single)
            if book_doc == []:
                info = '书籍均已上架'
                return raise_status(400, info)
            es_bulk('t_books', book_doc)
            redis_zincrby(category_list, 1)
        elif action == 'down':
            category_list = []
            for book_id in list:
                operation = {session['id']: [session['username'], 'down', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]}
                db.t_books.update({'_id': ObjectId(book_id)}, {'$push': {'operation': operation}})
                db.t_books.update({'_id': ObjectId(book_id)}, {'$set': {'shelf_status': '0',
                                                                        'change_status': '0', 'check_status': '0'}})
                # 书籍下架时，书籍下的书摘也都下架，下架后修改状态为未修改、审核状态为未审核
                db.t_excerpts.update({'bookid': book_id}, {'$push': {'operation': operation}})
                db.t_excerpts.update({'bookid': book_id}, {'$set': {'shelf_status': '0',
                                                                 'change_status': '0', 'check_status': '0'}})
                es_delete('t_books', book_id)
                data_down = db.t_books.find_one({'_id': ObjectId(book_id)})
                for single in data_down['category']:
                    category_list.append(single)
            redis_zincrby(category_list, -1)
        elif action == 'pass':
            for book_id in list:
                operation = {session['id']: [session['username'], 'pass', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]}
                data = db.t_books.find_one({'_id': ObjectId(book_id)})
                if data.get('change_status') == '2':
                    db.t_excerpt.remove({'bookid': ObjectId(book_id)})
                    db.t_books.remove({'_id': ObjectId(book_id)})
                if data.get('ck_book_name'):
                    data['book_name'] = data['ck_book_name']
                if data.get('ck_author_list'):
                    data['author_list'] = data['ck_author_list']
                if data.get('ck_category'):
                    data['category'] = data['ck_category']
                if data.get('ck_catalog_info'):
                    data['catalog_info'] = data['ck_catalog_info']
                if data.get('ck_tags'):
                    data['tags'] = data['ck_tags']
                if data.get('ck_summary'):
                    data['summary'] = data['ck_summary']
                if data.get('ck_cover_thumbnail'):
                    data['cover_thumbnail'] = data['ck_cover_thumbnail']
                if data.get('ck_score'):
                    data['score'] = data['ck_score']
                if data.get('ck_publish_info'):
                    data['publish_info'] = data['ck_publish_info']
                data['check_status'] = '1'
                db.t_books.update({'_id': ObjectId(book_id)}, {'$push': {'operation': operation}})
                db.t_books.update({'_id': ObjectId(book_id)}, data)
        elif action == 'refuse':
            for book_id in list:
                operation = {session['id']: [session['username'], 'refuse', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]}
                db.t_books.update({'_id': ObjectId(book_id)}, {'$push': {'operation': operation}})
                db.t_books.update({'_id': ObjectId(book_id)}, {'$set': {'check_status': '0', 'change_status': '0'}})
        returnObj['info'] = '操作成功'
        if key_status == 1:
            return raise_status(400, info)
        return jsonify(returnObj)
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '- book_operation error as: ', e)
        return raise_status(500, str(e))

# 删除书籍
@book.route('/book/del', methods=['DELETE'])
@sign_check()
def book_delete():
    from app import db
    returnObj = {}
    try:
        book_list = request.json.get('book_list')
        for book_id in book_list:
            db.t_books.update({'_id': ObjectId(book_id)}, {'$set': {'change_status': '2'}})
        returnObj['info'] = '操作成功'
        return jsonify(returnObj)
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '- book_delete error as: ', e)
        raise_status(500, str(e))

# 书籍封面
@book.route('/book/image/<book_id>', methods=['POST'])
# @sign_check()
def book_image(book_id):
    from app import db
    returnObj = {}
    try:
        type = request.args.get('type')
        allowed_extensions = set(['png', 'jpg', 'JPG', 'PNG', 'gif', 'GIF'])
        file = request.files.get('file')
        extension = file.filename.rsplit('.', 1)[1]
        if extension in allowed_extensions:
            message = img_bulk(file, extension)
            if type == '0':
                db.t_books.update({'_id': ObjectId(book_id)}, {'$set': {'ck_cover_thumbnail': message}})
                returnObj['info'] = '操作成功'
            elif type == '1':
                db.t_books.update({'_id': ObjectId(book_id)}, {'$set': {'cover_thumbnail': message}})
                returnObj['info'] = '操作成功'
        else:
            info = '图片格式不对'
            return raise_status(400, info)
        return jsonify(returnObj)
    except Exception as e:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '- book_image error as: ', e)
        raise_status(500, str(e))
