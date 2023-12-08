import functools
import datetime
import jwt
from flask import Blueprint
from jwt import exceptions
from flask import g, current_app, session, request

# from app import app
# 从Flask导入Blueprint类，实例化这个类就获得了我们的蓝本对象。
JWT = Blueprint("JWT", __name__)

SALT = 'iv%i6xo7l8_t9bf_u!8#g#m*)*+ej@bek6)(@u3kh*42+unjv='
# 设置一个密钥用于加密 session 数据
headers = {
    'typ': 'jwt',
    'alg': 'HS256'
}


def create_token(username, password):
    # 构造payload
    payload = {
        'username': username,
        'password': password,  # 自定义用户ID
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)  # 超时时间
    }
    result = jwt.encode(payload=payload, key=SALT, algorithm="HS256", headers=headers)
    return result


def verify_jwt(token, secret=None):
    """
    检验jwt
    :param token: jwt
    :param secret: 密钥
    :return: dict: payload
    """
    if not secret:
        secret = current_app.config['JWT_SECRET']

    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except exceptions.ExpiredSignatureError:  # 'token已失效'
        return 1
    except jwt.DecodeError:  # 'token认证失败'
        return 2
    except jwt.InvalidTokenError:  # '非法的token'
        return 3


def login_required(f):
    """
    使用functools模块的wraps装饰内部函数
    """

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            if g.username == -1:
                # print('error1')
                return {'message': 'token已失效'}, 401
            elif g.username == -2:
                # print('error2')
                return {'message': 'token认证失败'}, 401
            elif g.username == -3:
                # print('error3')
                return {'message': '非法的token'}, 401
            else:
                return f(*args, **kwargs)
        except Exception as e:
            print(e)
            return {'message': '请先登录认证.'}, 401

    '第2种方法,在返回内部函数之前,先修改wrapper的name属性'
    # wrapper.__name__ = f.__name__
    return wrapper





def jwt_authentication():
    """
    1.获取请求头Authorization中的token
    2.判断是否以 Bearer开头
    3.使用jwt模块进行校验
    4.判断校验结果,成功就提取token中的载荷信息,赋值给g对象保存
    """
    auth = request.headers.get('Authorization')

    if auth and auth.startswith('Bearer '):
        "提取token 0-6 被Bearer和空格占用 取下标7以后的所有字符"
        token = auth[7:]
        "校验token"
        g.username = None
        try:
            "判断token的校验结果"
            payload = jwt.decode(token, SALT, algorithms=['HS256'])
            "获取载荷中的信息赋值给g对象"
            g.username = payload.get('username')
        except exceptions.ExpiredSignatureError:  # 'token已失效'
            g.username = -1
        except jwt.DecodeError:  # 'token认证失败'
            g.username = -2
        except jwt.InvalidTokenError:  # '非法的token'
            g.username = -3