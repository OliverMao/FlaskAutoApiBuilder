from flask import g
from sqlalchemy.orm import column_property, synonym

from Faab.extensions import db
from Faab.Mixin import FieldPermissionMixin


# 根据是否采用字段级权限控制，进行继承FieldPermissionMixin类
class Spu(FieldPermissionMixin, db.Model):
    __bind_key__ = 'test'
    __tablename__ = 'spu'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), default='')
    desc = db.Column(db.String(255), default='')
    price = db.Column(db.Integer, default=0)
    add_time = db.Column(db.DateTime, default=db.func.now())
    is_delete = db.Column(db.Integer, default=0)

    def accessible(self, user):
        # 根据user的角色或权限返回不同的字段列表
        if user.get_role() == 'admin':
            fields = ['id', 'name', 'desc', 'price', 'add_time']  # 管理员可以访问所有字段
            allow_other_row = True
        else:
            fields = ['id', 'name']  # 其他用户只能访问部分字段
            allow_other_row = True
        return {'fields': fields, 'allow_other_row': allow_other_row}


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
            allow_other_row = True
        else:
            fields = ['faab_uid', 'nickname']  # 其他用户只能访问部分字段
            allow_other_row = False
        return {'fields': fields, 'allow_other_row': allow_other_row}
