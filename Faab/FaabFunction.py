import json
from functools import wraps

from flasgger import swag_from
from flask import request, g
from sqlalchemy import and_
from sqlalchemy.orm import class_mapper
from flask_sqlalchemy import SQLAlchemy

from Faab.FaabJWT import login_required
from Faab.extensions import db


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
                if key == "_Own":
                    continue
                exists = self.check_parameter_exists(key)
                if not exists:
                    return {'error': 'a参数错误', 'code': 11}
            for key, value in need_update.items():
                exists = self.check_parameter_exists(key)
                if not exists:
                    return {'error': 'b参数错误', 'code': 10}
            # noinspection PyCallingNonCallable
            return func(self, *args, **kwargs)

        return wrapper

    def check_parameter_exists(self, parameter):
        mapper = class_mapper(self.model)
        return hasattr(mapper.column_attrs, parameter)

    @swag_from('swag_config/get.yml')
    def get(self):
        """
        根据请求参数获取数据

        从请求参数中获取参数，过滤参数，根据参数进行查询，并返回结果

        Args:
            self: 对象本身

        Returns:
            dict: 包含数据的字典

        Remark：

        如果请求参数中包含_Not_Filter，则根据_Not_Filter的值进行过滤操作。
        如果请求参数中包含_Own，则将数据中的name字段替换为当前用户的用户名。
        如果请求参数中包含_Pagination，则使用分页方式进行查询。
        在查询数据之前，根据不同的请求参数，进行一些过滤操作。
        如果请求参数中包含_Search，则根据_Search的值进行模糊查询。根据其他请求参数进行精确查询。
        如果过滤操作不为False，则根据对应的键值对进行过滤操作。
        根据过滤后的条件，使用filter函数过滤查询结果。
        如果没有进行分页查询，使用all函数获取所有过滤后的数据，并返回。
        如果进行了分页查询，使用paginate函数进行分页查询。获取分页结果中的数据、分页信息，并将其组织成一个字典，返回给客户端。

        """
        params = dict(request.args)  # 获取请求参数
        _Not_Filter = False

        if '_Not_Filter' in params:
            _Not_Filter = json.loads(params.pop('_Not_Filter'))

        print(params)

        if '_Own' in params:
            name = params.get('_Own')
            params[name] = g.username
            params.pop('_Own')

        if '_Pagination' not in params:
            if '_Desc' not in params:
                query = self.model.query.filter_by(is_delete=0)
            else:
                query = self.model.query.filter_by(is_delete=0).order_by(self.model.id.desc())
                params.pop('_Desc')

            filters = []

            if '_Search' in params:
                key = params.pop('_Search')
                value = params.pop('_Search_value')
                filters.append(getattr(self.model, key).like('%' + value + '%'))

            for key, value in params.items():
                filters.append(getattr(self.model, key) == value)

            if _Not_Filter != False:
                filters.append(getattr(self.model, _Not_Filter['key']) != _Not_Filter['value'])

            if filters:
                query = query.filter(and_(*filters))

            lists = query.all()  # 执行查询

            return self.list_to_return(lists)
        else:
            params.pop('_Pagination')
            page = int(params.pop('page'))
            per_page = int(params.pop('per_page'))
            if '_Desc' not in params:
                query = self.model.query.filter_by(is_delete=0)
            else:
                query = self.model.query.filter_by(is_delete=0).order_by(self.model.id.desc())
                params.pop('_Desc')

            filters = []

            if '_Search' in params:
                key = params.pop('_Search')
                value = params.pop('_Search_value')
                filters.append(getattr(self.model, key).like('%' + value + '%'))

            for key, value in params.items():
                filters.append(getattr(self.model, key) == value)

            if _Not_Filter != False:
                filters.append(getattr(self.model, _Not_Filter['key']) != _Not_Filter['value'])

            if filters:
                query = query.filter(and_(*filters))

            lists = query.paginate(page=page, per_page=per_page, error_out=False)  # 执行分页查询

            items = lists.items
            has_next = lists.has_next
            has_prev = lists.has_prev
            total = lists.total
            pages = lists.pages

            return {'items': self.list_to_return(items), 'has_next': has_next, 'has_prev': has_prev, 'total': total,
                    'pages': pages}


    @swag_from('swag_config/get_one.yml')
    def get_one(self):
        params = dict(request.args)
        if '_Own' in params:
            name = params.get('_Own')
            params[name] = g.username
            params.pop('_Own')
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
        if '_Own' in condition:
            name = condition.get('_Own')
            condition[name] = g.username
            condition.pop('_Own')
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
