from flasgger import swag_from

from flask.views import MethodView
from flask import request

from ..test import test_bp, model
from Faab.FaabJWT import create_token
from Faab.extensions import db


# 注册
@test_bp.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    name = request.json.get('name')
    user_info = model.Users.query.filter_by(username=username).first()
    if user_info:
        return "该用户已存在"
    else:
        user = model.Users(username=username, password=password, name=name)
        db.session.add(user)
        db.session.commit()
        return "注册成功"


@test_bp.route('/login',methods=['POST'])
def login():
    user_name = request.json.get('username')
    password = request.json.get('password')
    user_info = model.Users.query.filter_by(username=user_name, password=password).first()
    if user_info:
        token = 'Bearer '+create_token('admin', "user")
        return token
    else:
        return "错误"


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
