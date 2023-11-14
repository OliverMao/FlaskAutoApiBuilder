from flasgger import swag_from

from flask.views import MethodView
from flask import request

from blueprints.test import test_bp



class MyAPI(MethodView):
    @swag_from('swag_config/get.yml')
    def get(self):
        # 处理GET请求的逻辑
        return "GET请求"

    def post(self):
        # 处理POST请求的逻辑
        data = request.json
        return "POST请求: {}".format(data)

    def put(self):
        # 处理PUT请求的逻辑
        return "PUT请求"

    def delete(self):
        # 处理DELETE请求的逻辑
        return "DELETE请求"


test_bp.add_url_rule('/', view_func=MyAPI.as_view('my_api'))
