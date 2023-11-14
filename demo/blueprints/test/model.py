from Faab.extensions import db

class Users(db.Model):
    __bind_key__ = 'test'
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True)
    name = db.Column(db.String(255), default='')
    password = db.Column(db.String(255))
    avatar = db.Column(db.Text(1000), default='')
    is_delete = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<users %r>' % self.username


class TabNavMenu(db.Model):
    __bind_key__ = 'test'
    __tablename__ = 'tabnavmenu'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), default='')
    icon = db.Column(db.String(255), default='')
    target = db.Column(db.Text(1000), default='/pages/index/index')
    state = db.Column(db.Integer, default=1)  # 1为正常使用 0为封禁

    def __repr__(self):
        return self.id


