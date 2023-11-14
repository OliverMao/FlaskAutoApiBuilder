import json
from functools import wraps

from flasgger import swag_from
from flask import request
from sqlalchemy import and_
from sqlalchemy.orm import class_mapper
from flask_sqlalchemy import SQLAlchemy

from Faab.FaabJWT import login_required

# 扩展类实例化
db = SQLAlchemy()


# ......

class AutoUrl:
    def __init__(self, add_url_list):
        for i in add_url_list:
            AutoDB(i["model"], i["bp"], i["url_prefix"])


class AutoDB:
    model = {}
    bp = object
    url_name = ""

    def __init__(self, model, bp, url_name):

        self.model = model
        self.bp = bp
        self.url_name = url_name
        self.bp.add_url_rule('/' + url_name + '/get', endpoint=bp.name + url_name + 'get',
                             view_func=self.get,
                             methods=['GET'])
        self.bp.add_url_rule('/' + url_name + '/get_one', endpoint=bp.name + url_name + 'get_one',
                             view_func=self.get_one,
                             methods=['GET'])
        self.bp.add_url_rule('/' + url_name + '/post', endpoint=bp.name + url_name + 'post',
                             view_func=self.post,
                             methods=['POST'])
        self.bp.add_url_rule('/' + url_name + '/delete/<int:one_or_list>/<int:true_del_or_false_del>',
                             endpoint=bp.name + url_name + 'delete', view_func=self.delete,
                             methods=['POST'])
        self.bp.add_url_rule('/' + url_name + '/put', endpoint=bp.name + url_name + 'put',
                             view_func=self.put,
                             methods=['POST'])

    def list_to_return(self, get_list):
        """
            FuncName:列表转返回值
            Parameter：查询出的结果
            Return：Http返回值
        """
        result = []
        for item in get_list:
            data = {}
            for col in class_mapper(self.model).mapped_table.c:
                value = str(getattr(item, col.name))
                if value != 'None':
                    data[col.name] = value
                else:
                    continue
            result.append(data)
        return result

    def one_to_return(self, info):
        """
            FuncName:单个数据转返回值
            Parameter：查询出的结果
            Return：Http返回值
        """
        data = {}
        for col in class_mapper(self.model).mapped_table.c:
            value = str(getattr(info, col.name))
            if value != 'None':
                data[col.name] = value
            else:
                continue
        return data

    # noinspection ALL
    def check_request_delete(func):
        # noinspection PyTypeChecker
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            params = request.json
            for key, value in params.items():
                exists = self.check_parameter_exists(key)
                if not exists:
                    return {'error': '参数错误', 'code': 0}
            # noinspection PyCallingNonCallable
            return func(self, *args, **kwargs)

        return wrapper

    # noinspection ALL
    def check_request_turn(func):
        # noinspection PyTypeChecker
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            form = request.json
            need_update = form.get('need_update')
            condition = form.get('condition')
            for key, value in condition.items():
                exists = self.check_parameter_exists(key)
                if not exists:
                    return {'error': '参数错误', 'code': 0}
            for key, value in need_update.items():
                exists = self.check_parameter_exists(key)
                if not exists:
                    return {'error': '参数错误', 'code': 0}
            # noinspection PyCallingNonCallable
            return func(self, *args, **kwargs)

        return wrapper

    def check_parameter_exists(self, parameter):
        mapper = class_mapper(self.model)
        return hasattr(mapper.column_attrs, parameter)

    @swag_from('swag_config/get.yml')
    def get(self):
        params = dict(request.args)
        if 'order_by' not in params:
            query = self.model.query.filter_by(is_delete=0)
        else:
            order_by = params.get('order_by')
            if order_by == 'desc':
                query = self.model.query.filter_by(is_delete=0).order_by(self.model.id.desc())
            else:
                query = self.model.query.filter_by(is_delete=0)
            params.pop('order_by')
        filters = []

        for key, value in params.items():
            filters.append(getattr(self.model, key) == value)

        if filters:
            query = query.filter(and_(*filters))
        lists = query.all()

        return self.list_to_return(lists)

    @swag_from('swag_config/get_one.yml')
    def get_one(self):
        params = dict(request.args)
        filters = []
        query = self.model.query.filter_by(is_delete=0)
        for key, value in params.items():
            filters.append(getattr(self.model, key) == value)

        if filters:
            query = query.filter(and_(*filters))
        item = query.first()

        return self.one_to_return(item)

    @swag_from('swag_config/post.yml')
    def post(self):
        sets = request.json
        new_item = self.model()
        for key, value in sets.items():
            setattr(new_item, key, value)
        try:
            db.session.add(new_item)
            db.session.commit()
            return {'id': new_item.id, 'code': 1}
        except Exception as e:
            print(e)
            return {'error': e, 'code': -1}

    # noinspection PyArgumentList
    @swag_from('swag_config/delete.yml')
    @check_request_delete
    def delete(self, one_or_list=1, true_del_or_false_del=0):
        params = request.json
        query = self.model.query.filter_by(is_delete=0)
        filters = []
        for key, value in params.items():
            filters.append(getattr(self.model, key) == value)

        if filters:
            query = query.filter(and_(*filters))

        if len(query.all()) > 0:
            if one_or_list == 1:
                if true_del_or_false_del == 0:
                    info = query.first()
                    info.is_delete = 1
                else:
                    query.delete()
            else:
                if true_del_or_false_del == 0:
                    query = query.all()
                    for i in query:
                        i.is_delete = 1
                else:
                    query.delete(synchronize_session=False)
            try:
                db.session.commit()
                return {'code': 1, 'message': '已成功删除'}
            except Exception as e:
                return {'error': e, 'code': -1}
        else:
            return {'error': '未查询到数据', 'code': 0}

    # noinspection PyArgumentList
    @swag_from('swag_config/put.yml')
    @check_request_turn
    def put(self):
        form = request.json
        query = self.model.query.filter_by(is_delete=0)
        filters = []
        need_update = form.get('need_update')
        condition = form.get('condition')
        for key, value in condition.items():
            filters.append(getattr(self.model, key) == value)
        if filters:
            query = query.filter(and_(*filters))
        if len(query.all()) > 0:
            for i in query:
                for key, value in need_update.items():
                    setattr(i, key, value)
            try:
                db.session.commit()
                return {'code': 1, 'message': '已成功更新', 'num': len(query.all())}
            except Exception as e:
                return {'error': e, 'code': -1}
        else:
            return {'error': '未查询到匹配数据', 'code': 0}
