

<div align="center"><a href="https://github.com/OliverMao/FlaskAutoApiBuilder" ><img width="300" src="https://z1.ax1x.com/2023/11/14/piYkvUU.png" alt="piYkvUU.png" border="0" /></a>
<h1> 📦 Faab - Flask Auto API Builder</h1><div><a href="https://github.com/OliverMao/FlaskAutoApiBuilder" ><img  src="https://img.shields.io/badge/license-GPL3.0-blue.svg" alt="license" border="0" /></a>
  <img  src="https://img.shields.io/github/stars/OliverMao/FlaskAutoApiBuilder.svg" alt="stars" border="0" />
  <img  src="https://img.shields.io/github/forks/OliverMao/FlaskAutoApiBuilder.svg" alt="forks" border="0" />
  <img  src="https://img.shields.io/badge/version-0.1.6-686480r.svg" alt="forks" border="0" />
</div></div>







## 项目简介

"Flask Auto API Builder" 是一个基于 Flask 框架的自动 API 构建工具。

本工具可以根据给定的数据模型或数据库模式自动生成 API 端点，包括创建、读取、更新和删除（CRUD）操作。它们可以减少开发人员手动编写和配置 API 端点的工作量，提高开发效率。同时可以生成Swagger文档，便于API调试。此外，Faab还提供了常见的Web工具，如用户鉴权、上传下载等功能，进一步增强了开发者的体验。

## 功能特性

- 用户身份验证：通过用户名和密码进行用户身份验证，确保只有授权用户可以访问受保护的功能。
- 创建资源：允许用户创建新的资源，例如创建新的文章、任务或事件等。
- 读取资源：提供对已存在资源的读取访问权限，例如获取文章的详细信息或查看任务列表。
- 更新资源：允许用户对现有资源进行更新，例如编辑文章内容或修改任务状态。
- 删除资源：允许用户删除不再需要的资源，例如删除文章、任务或事件等。
- 搜索功能：提供基于关键字的搜索功能，使用户能够快速找到所需的资源。
- 分页和排序：支持对资源列表进行分页和排序，以便用户可以方便地浏览和管理大量数据。
- 文件上传和下载：允许用户上传文件到服务器，并提供下载已上传的文件的功能。
- 数据验证：对用户输入的数据进行验证，确保数据的完整性和一致性。
- 错误处理：提供友好的错误提示和处理机制，使用户能够轻松识别和解决问题。
- 访问控制：基于用户角色和权限，限制用户对敏感资源和功能的访问权限。
- 日志记录：记录关键操作和事件，以便进行故障排查和审计。
- API 文档生成：自动生成 API 文档，使开发人员和用户能够了解可用的 API 端点和参数。

## 技术栈与依赖项

- Flask
- SQLAlchemy
- flasgger
- PyJWT
- Flask-CORS
- Redis
- PyMySQL
- RPC
- Flask-JSONRPC
- FFmpeg

## 快速开始

0. 创建app.py
1. 创建factory.py、blueprints（根据开发项目自定）
	
	> 可直接使用Faab提供的demo进行开发
	
2. 安装Faab：
    ```
    pip install Faab
    ```
3. 项目中引入
    ```python
    from Faab import Faab
    
    from Faab.FaabJWT import jwt_authentication
    from blueprints.test import test_bp
    from blueprints.test.model import Users, TabNavMenu
    import factory as fac 
    ```
4. 配置数据库连接
	> 一定要新建一个名为faab的数据库
   
    ```python
    class DBConfig(object):
        # DB及Flask基础配置
        user = 'faab'
        host = 'localhost'
        password = 'faab'
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:3306/%s' % (user, password, host, 'faab')
        SQLALCHEMY_BINDS = {
            'test': 'mysql+pymysql://%s:%s@%s:3306/%s' % (user, password, host, 'test')
        }
        SECRET_KEY = 'session_key'
    ```
5. 配置AutoAPI Model与蓝图
	```python
	class Spu(db.Model):
    __bind_key__ = 'test'
    __tablename__ = 'spu'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), default='')
    desc = db.Column(db.String(255), default='')
    price = db.Column(db.Integer, default=0)
    add_time = db.Column(db.DateTime, default=db.func.now())
    is_delete = db.Column(db.Integer, default=0)
	
    class Users(FieldPermissionMixin, db.Model):
        __bind_key__ = 'test'
        __tablename__ = 'users'
        __table_args__ = {'extend_existing': True}
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        faab_uid = db.Column(db.String(255), unique=True)
        username = db.Column(db.String(255), unique=True)
        password = db.Column(db.String(255))
        nickname = db.Column(db.String(255), default='')
        is_delete = db.Column(db.Integer, default=0)
	
        def accessible(self, user):
           # 根据user的角色或权限返回不同的字段列表
           if user.get_role() == 'admin':
               fields = ['faab_uid', 'nickname', 'username', 'password', 'id']  # 管理员可以访问的字段
               allow_other_row = True  # 允许访问非此faab_uid的行
           else:
	            fields = ['faab_uid', 'nickname']  # 其他用户只能访问部分字段
	            allow_other_row = False  # 不允许访问非此faab_uid的行
	        return {'fields': fields, 'allow_other_row': allow_other_row}
   
   ```
   根据是否需要字段级权限控制，进行数据表model是否继承FieldPermissionMixin类。如继承类，则_Need_keys查询对权限字段进行交集处理后返回。
   
    ```python
    models = [
        [
            {
                "model": your_model,
                "bp": your_blueprints,
                "url_prefix": "your_url_prefix"
            }
        ]
    ]
    
    app = Faab(__name__)
    app.add_models(models)
    app.add_db_config(DBConfig)
    fac.register(app) #可选
    ```
6. 配置启动参数
    ```python
    if __name__ == '__main__':
        app.run(debug=True, port=5000, host='0.0.0.0')
    ```
7. 运行
    ```shell
    python app.py
    ```
8. 在浏览器中访问Swagger文档：
   ```
   http://localhost:5000/apidocs
   ```


## Faab开发文档

详细的文档将在正式版更新。

## RPC

对于用户权限控制，采用了总表的方式，位于faab数据库的faab_users表内进行了身份权限的控制管理。faab_users表采用了Snowflake，方便分布式系统对用户的UID进行管理。如使用字段权限管理，在用户注册时请调用RPC接口如
```python
url = 'http://127.0.0.1:8011/rpc'
payload = {
"jsonrpc": "2.0",
"method": "FaabRegister",
"params": {"username": username, "password": password, "role": "user"},
"id": 1
}
```
result返回值code:200为正确加入，其余情况请勿添加新用户。对于用户权限名称，例如admin、user，均由开发者进行控制，访问权限于model中进行管理。

## 开源不易, 有了您的赞助, 我们会做的更好~

  <img src="./static/donate.jpg" alt style="width: 20%;">


## 许可证

本项目采用 GNU 通用公共许可证（GNU General Public License，简称 GPL）进行许可。这意味着您有权使用、复制、修改和分发本项目的源代码和衍生作品，但需要遵守以下条件：

1. 版权声明：您需要在您的衍生作品中包含原始项目的版权声明和许可证信息。

2. 开放源代码：如果您对本项目进行修改或扩展，并将其作为衍生作品分发，您需要以相同的许可证（GPL）分发您的修改和源代码。

3. 无保证：该项目没有任何明示或暗示的保证。作者不对项目的适用性、可靠性或准确性提供任何保证，亦不承担任何责任。您自担风险使用本项目。

4. 贡献：如果您对本项目进行贡献，您同意将您的贡献授予原始项目的所有者，并同意您的贡献将在原始项目的 GPL 许可下分发。

有关完整的许可证文本，请参阅项目根目录中的 LICENSE 文件。

## 技术反馈与交流群

  <img src="./static/official.jpg" alt style="width: 20%;">

- 加入交流群交流
- 获取Faab开发教程文章
- 与作者进行相关交流



