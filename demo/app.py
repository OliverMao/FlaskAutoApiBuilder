# Faab Project Demo

from Faab import Faab
from Faab.FaabJWT import jwt_authentication
from blueprints.test import test_bp
from blueprints.test.model import Users
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
            "model": Users,
            "bp": test_bp,
            "url_prefix": "Users"
        }
    ]
]

app = Faab(import_name=__name__, static_url_path='/s')
app.add_models(models)
app.add_db_config(DBConfig)
fac.register(app)

@app.before_request
def auth():
    jwt_authentication()


if __name__ == '__main__':
    app.run(debug=True, port=8011, host='0.0.0.0')
