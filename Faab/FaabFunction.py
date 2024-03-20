import json
from functools import wraps

from flasgger import swag_from
from flask import request, g, send_file
from sqlalchemy import and_
from sqlalchemy.orm import class_mapper
from flask_sqlalchemy import SQLAlchemy

from Faab.FaabJWT import login_required
from Faab.extensions import db
import pandas as pd
import io


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
        self.bp.add_url_rule('/' + url_name + '/export', endpoint=bp.name + url_name + 'export',
                             view_func=self.export,
                             methods=['POST'])

    def list_to_return(self, get_list, need_keys=None):
        """
            FuncName:列表转返回值
            Parameter：查询出的结果
            Return：Http返回值
        """
        result = []
        for item in get_list:
            data = {}
            if need_keys:
                for col in need_keys:
                    value = str(getattr(item, col))
                    if value != 'None':
                        data[col] = value
                    else:
                        continue
            else:
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
    def check_request_export(func):
        # noinspection PyTypeChecker
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            form = request.json
            need_export = form.get('need_export')
            condition = form.get('condition')
            for key, value in condition.items():
                if key == "_Own" or key == "_Price":
                    continue
                exists = self.check_parameter_exists(key)
                if not exists:
                    return {'error': 'a参数错误', 'code': 11}
            for key, value in need_export.items():
                exists = self.check_parameter_exists(key)
                if not exists:
                    return {'error': 'b参数错误', 'code': 10}
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
        params = dict(request.args)
        _Not_Filter = False
        pagination = False
        page = 0
        per_page = 0
        if '_Pagination' in params:
            pagination = True
            params.pop('_Pagination')
            page = int(params.pop('page'))
            per_page = int(params.pop('per_page'))
        if '_Not_Filter' in params:
            _Not_Filter = json.loads(params.pop('_Not_Filter'))
        if '_Own' in params:
            name = params.get('_Own')
            params[name] = g.username
            params.pop('_Own')

        if '_Desc' not in params:
            if '_Order' not in params:
                query = self.model.query.filter_by(is_delete=0)
            else:
                order_key = params.pop('_Order')
                column = getattr(self.model, order_key)
                query = self.model.query.filter_by(is_delete=0).order_by(column)
        else:
            desc_key = params.pop('_Desc')
            column = getattr(self.model, desc_key)
            query = self.model.query.filter_by(is_delete=0).order_by(column.desc())
        filters = []
        if "_Range" in params:
            info = json.loads(params.pop('_Range'))
            key = info['key']
            if 'min' in info:
                filters.append(getattr(self.model, key) >= int(info['min']))
            if 'max' in info:
                filters.append(getattr(self.model, key) <= int(info['max']))
        if '_Search' in params:
            key = params.pop('_Search')
            value = params.pop('_Search_value')
            filters.append(getattr(self.model, key).like('%' + value + '%'))

        get_resu_num = ''
        if '_Get_resu_num' in params:
            get_resu_num = params.pop('_Get_resu_num')

        need_keys = ''
        if '_Need_keys' in params:
            need_keys = params.pop('_Need_keys').split(',')

        for key, value in params.items():
            filters.append(getattr(self.model, key) == value)

        if _Not_Filter != False:
            filters.append(getattr(self.model, _Not_Filter['key']) != _Not_Filter['value'])

        if filters:
            query = query.filter(and_(*filters))
        if not pagination:
            if get_resu_num:
                lists = query.limit(get_resu_num)
            else:
                lists = query.all()
            return self.list_to_return(lists, need_keys)
        else:
            lists = query.paginate(page=page, per_page=per_page, error_out=False)
            items = lists.items
            has_next = lists.has_next
            has_prev = lists.has_prev
            total = lists.total
            pages = lists.pages
            return {'items': self.list_to_return(items, need_keys), 'has_next': has_next, 'has_prev': has_prev, 'total': total,
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

    # noinspection PyArgumentList
    @swag_from('swag_config/export.yml')
    @check_request_export
    def export(self):
        form = request.json
        query = self.model.query.filter_by(is_delete=0)
        filters = []
        need_export = form.get('need_export')
        condition = form.get('condition')
        _Price = []
        if "_Price" in form:
            # 金额化处理
            _Price = form.get('_Price').split(',')
        if '_Own' in condition:
            name = condition.get('_Own')
            condition[name] = g.username
            condition.pop('_Own')
        for key, value in condition.items():
            filters.append(getattr(self.model, key) == value)
        if filters:
            query = query.filter(and_(*filters))
        db_list = query.all()
        if len(db_list) > 0:
            try:
                return export_to_excel(db_list, need_export, _Price)
            except Exception as e:
                return {'error': e, 'code': -1}
        else:
            return {'error': '未查询到匹配数据', 'code': 0}


def export_to_excel(db_list, need_export, _Price):
    # 将查询结果转换为DataFrame
    out_data = []
    i = 1
    for obj in db_list:
        data = {}
        data.update({'序号': i})
        for key, value in need_export.items():
            if key in _Price:
                data.update({value: str('{:.2f}'.format(getattr(obj, key) / 100))})
            else:
                data.update({value: str(getattr(obj, key))})
        out_data.append(data)
        i += 1
    df = pd.DataFrame(out_data)

    # 将数据表导出为XLSX文件
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer._save()
    output.seek(0)
    # 返回XLSX文件供下载
    resu = send_file(output, download_name='exported_data.xlsx', as_attachment=True)
    return resu
