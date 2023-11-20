from flask import Flask
from flask_cors import *
import typing as t
# 初始化
from .factory import create_app
from Faab.__version__ import VERSION as version


class faab(Flask):
    _startup_message_printed = False
    models = []
    db_config = object()
    need_register_bp = []

    def __init__(self, import_name: str):
        # 初始化函数，接收一个字符串类型的参数import_name
        super().__init__(import_name)

    def add_models(self, model: list):
        # 添加模型函数，接收一个列表类型的参数model
        self.models = model

    def add_db_config(self, db_config: object):
        # 添加数据库配置函数，接收一个对象类型的参数db_config
        self.db_config = db_config

    def add_blueprints(self, blueprint: list):
        # 添加蓝图函数，接收一个列表类型的参数blueprint
        self.need_register_bp = blueprint

    def run(
            self,
            host: str | None = None,
            port: int | None = None,
            debug: bool | None = None,
            load_dotenv: bool = True,
            **options: t.Any,
    ) -> None:
        """
           Run the Flask server.

           :param host: The host address the server should bind to.
           :param port: The port the server should run on.
           :param debug: Whether to run in debug mode.
           :param load_dotenv: Whether to load the `.env` file.
           :param options: Additional options to pass to the server.
        """
        create_app(app=self, models=self.models, db_config=self.db_config, url_prefix="/api",
                   blueprints=self.need_register_bp)
        CORS(self, resources=r'/*')
        self._print_startup_message()
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
