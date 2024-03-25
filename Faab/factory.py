from flask import Flask
from Faab.extensions import db
from Faab.FaabJWT import JWT
from flasgger import Swagger
import inspect
from Faab.FaabFunction import AutoUrl


def get_variable_name(obj):
    # 遍历当前作用域的变量
    frame = inspect.currentframe().f_back
    # 遍历当前帧的变量
    for name, value in frame.f_locals.items():
        if value is obj:
            return name
    return None


def create_app(app, models, db_config, url_prefix: str | None = '/api', blueprints=None):
    app.config.from_object(db_config)
    # 注册蓝本
    if len(blueprints) > 0:
        for bp in blueprints:
            app.register_blueprint(bp, url_prefix=url_prefix + '/' + bp.name)
    for model in models:
        AutoUrl(model)
        app.register_blueprint(model[0]["bp"], url_prefix=url_prefix + '/' + model[0]["bp"].name)
    app.register_blueprint(JWT)

    # 初始化扩展
    db.init_app(app)

    # Swagger
    swagger_config = Swagger.DEFAULT_CONFIG
    swagger_config['title'] = 'Faab'  # 配置大标题
    swagger_config['description'] = '由Faab自动生成的API文档'  # 配置公共描述内容
    swagger_config['version'] = '1.0.0'  # 配置版本
    Swagger(app, config=swagger_config)
    with app.app_context():
        # 在应用程序上下文中执行需要应用程序的操作
        # db.drop_all()
        db.create_all()
    return app


