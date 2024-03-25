import requests
from flasgger import swag_from

from flask.views import MethodView
from flask import request

from ..test import test_bp, model
from Faab.FaabJWT import create_token
from Faab.extensions import db
from Faab.Mixin import FaabUsers


# 注册
@test_bp.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    nickname = request.json.get('nickname')
    user_info = model.Users.query.filter_by(username=username).first()
    if user_info:
        return "该用户已存在"
    else:
        url = 'http://127.0.0.1:8011/rpc'
        payload = {
            "jsonrpc": "2.0",
            "method": "FaabRegister",
            "params": {"username": username, "password": password, "role": "user"},
            "id": 1
        }
        response = requests.post(url, json=payload)
        result = response.json()['result']
        if result['code'] == 0:
            return '该用户已存在'
        elif result['code'] == 200:
            user = model.Users(username=username, password=password, nickname=nickname, faab_uid=result['uid'])
            db.session.add(user)
            db.session.commit()
            return "注册成功"


@test_bp.route('/login',methods=['POST'])
def login():
    user_name = request.json.get('username')
    password = request.json.get('password')
    user_info = FaabUsers.query.filter_by(username=user_name, password=password).first()
    if user_info:
        token = 'Bearer '+create_token(username=user_name, uid=user_info.uid)
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
