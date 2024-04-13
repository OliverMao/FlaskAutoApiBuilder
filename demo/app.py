# Faab Project Demo

from Faab import Faab
from Faab.FaabJWT import jwt_authentication
from blueprints.test import test_bp
from blueprints.test.model import Spu, Users, Order
import factory as fac


class DBConfig(object):
    # 基础配置
    user = 'faab'
    host = 'localhost'
    password = 'faab'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:3306/%s' % (user, password, host, 'faab')
    SQLALCHEMY_BINDS = {
        'test': 'mysql+pymysql://%s:%s@%s:3306/%s' % (user, password, host, 'test')
    }
    SECRET_KEY = 'session_key'


models = [
    [
        {
            "model": Spu,
            "bp": test_bp,
            "url_prefix": "spu",
        },
{
            "model": Users,
            "bp": test_bp,
            "url_prefix": "users",
        },{
            "model": Order,
            "bp": test_bp,
            "url_prefix": "order",
        }
    ]
]

app = Faab(import_name=__name__, static_url_path='/s')
app.add_models(models)
app.add_db_config(DBConfig)
fac.register(app)
app.add_rpc()
app.faab_ready()
application = app  # uWSGI启动必须有application


@app.before_request
def auth():
    jwt_authentication()


if __name__ == '__main__':
    app.run(port=8011, host='0.0.0.0')
