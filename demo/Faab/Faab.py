from functools import partial

from flask import Flask
from flask_cors import *
import typing as t

from flask_jsonrpc import JSONRPC

from .Mixin import FaabUsersFunction, SnowflakeIdGenerator
# 初始化
from .factory import create_app
from Faab.__version__ import VERSION as version


class Faab(Flask):
    _startup_message_printed = False
    models = []
    db_config = object()
    need_register_bp = []

    def __init__(self, **options):
        # 调用父类的__init__方法，并传递其他参数
        super().__init__(**options)

        # TODO 调整rpc实例

    def add_rpc(self, machine_id=1, datacenter_id=1):
        # 创建实例，设定机器ID和数据中心ID
        generator = SnowflakeIdGenerator(machine_id=machine_id, datacenter_id=datacenter_id)
        faab_users_function = FaabUsersFunction(generator)

        def faab_register_wrapper(username: str, password: str, role: str) -> t.Any:
            return faab_users_function.faab_register(username, password, role)

        jsonrpc = JSONRPC(self, '/rpc', enable_web_browsable_api=True)
        # 添加一个RPC_URL规则，用于注册用户
        jsonrpc.register(view_func=faab_register_wrapper, name='FaabRegister')
        # self.add_url_rule('/rpc/faab/register', endpoint='FaabRegister', view_func=view_func,
        #                   methods=['POST']
        #                   )

    def add_models(self, model: list):
        # 添加模型函数，接收一个列表类型的参数model
        self.models = model

    def add_db_config(self, db_config: object):
        # 添加数据库配置函数，接收一个对象类型的参数db_config
        self.db_config = db_config

    def add_blueprints(self, blueprint: list):
        # 添加蓝图函数，接收一个列表类型的参数blueprint
        self.need_register_bp = blueprint

    def faab_ready(self):
        create_app(app=self, models=self.models, db_config=self.db_config, url_prefix="/api",
                   blueprints=self.need_register_bp)
        CORS(self, resources=r'/*')
        self._print_startup_message()

    def run(
            self,
            host: str | None = None,
            port: int | None = None,
            debug: bool | None = None,
            load_dotenv: bool = True,
            **options: t.Any,
    ) -> None:
        super().run(host, port, debug, load_dotenv, **options)

    def _print_startup_message(self):
        if not getattr(self, '_startup_message_printed', False):
            print("\033[1;32m * Faab Version:", version)
            print('''
    ███████╗ █████╗  █████╗ ██████╗      ██╗   ██╗ ██████╗  ██████╗ ██████╗ ██╗████████╗ ██████╗███╗   ██╗    
    ██╔════╝██╔══██╗██╔══██╗██╔══██╗     ╚██╗ ██╔╝██╔═══██╗██╔═══██╗██╔══██╗██║╚══██╔══╝██╔════╝████╗  ██║    
    █████╗  ███████║███████║██████╔╝█████╗╚████╔╝ ██║   ██║██║   ██║██████╔╝██║   ██║   ██║     ██╔██╗ ██║    
    ██╔══╝  ██╔══██║██╔══██║██╔══██╗╚════╝ ╚██╔╝  ██║   ██║██║   ██║██╔══██╗██║   ██║   ██║     ██║╚██╗██║    
    ██║     ██║  ██║██║  ██║██████╔╝        ██║   ╚██████╔╝╚██████╔╝██████╔╝██║   ██║██╗╚██████╗██║ ╚████║
            ''')

            self._startup_message_printed = True
