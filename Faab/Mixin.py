from flask import request, g
import time
import threading

from sqlalchemy.orm.collections import InstrumentedList

from Faab.extensions import db
from flask_jsonrpc import JSONRPC





class FieldPermissionMixin:
    def accessible(self, user):
        # 默认返回空集合，表示没有字段可访问
        # 子类应该覆盖这个方法来实现具体逻辑
        return dict()

    def to_dict(self, user, need_keys=None):
        # 根据用户权限，返回一个字典，包含可访问的字段
        access = self.accessible(user)
        fields = access['fields']
        allow_other_row = access['allow_other_row']
        if allow_other_row:
            # 如果允许查看其他行的数据，则返回所有字段
            if need_keys:
                # 获取need_keys和可访问权限的交集
                intersection = list(set(need_keys) & set(fields))
                result = {}
                for field in intersection:
                    # 如果是外键关联，则迭代
                    if issubclass(type(getattr(self, field)), InstrumentedList):
                        result[field] = self.list_to_return(getattr(self, field), user, need_keys)
                    else:
                        result[field] = getattr(self, field)
                return result
            else:
                result = {}
                for field in fields:
                    if issubclass(type(getattr(self, field)), InstrumentedList):
                        result[field] = self.list_to_return(getattr(self, field), user)
                    else:
                        result[field] = getattr(self, field)
                return result
        else:
            if user.uid == self.faab_uid:
                if need_keys:
                    result = {}
                    intersection = list(set(need_keys) & set(fields))
                    for field in intersection:
                        if issubclass(type(getattr(self, field)), InstrumentedList):
                            result[field] = self.list_to_return(getattr(self, field), user, need_keys)
                        else:
                            result[field] = getattr(self, field)
                    return result
                else:
                    result = {}
                    for field in fields:
                        if issubclass(type(getattr(self, field)), InstrumentedList):
                            result[field] = self.list_to_return(getattr(self, field), user)
                        else:
                            result[field] = getattr(self, field)
                    return result
                    # return {field: getattr(self, field) for field in fields}
            else:
                return {}

    @staticmethod
    def list_to_return(get_list, user, need_keys=None):
        datas = []
        for i in get_list:
            data = i.to_dict(user, need_keys)
            if data == {}:
                continue
            datas.append(data)
        return datas

class FaabUsers(FieldPermissionMixin, db.Model):
    __tablename__ = 'faab_users'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(255), unique=True)
    nickname = db.Column(db.String(255), default='')
    password = db.Column(db.String(255))
    role = db.Column(db.String(255), default='admin')
    is_delete = db.Column(db.Integer, default=0)

    def get_role(self):
        return self.role

    @staticmethod
    def faab_create_uid(generator):
        return generator.generate_id()


def get_current_user(uid):
    user = db.session.query(FaabUsers).filter(FaabUsers.uid == uid).first_or_404()
    return user


class FaabUsersFunction:
    def __init__(self, generator):
        self.generator = generator

    def faab_register(self, username, password, role):
        if FaabUsers.query.filter_by(username=username).first():
            return {'code': 0, 'msg': '用户名已存在'}, 409
        else:
            uid = FaabUsers.faab_create_uid(self.generator)
            user = FaabUsers(username=username, password=password, uid=uid, role=role)
            db.session.add(user)
            db.session.commit()
            return {'code': 200, 'msg': '注册成功', 'uid': uid}, 200


class SnowflakeIdGenerator:
    # 初始化开始时间戳（epoch），假定为2020-01-01
    epoch = 1577836800000
    # 机器ID
    machine_id_bits = 5
    # 数据中心ID
    datacenter_id_bits = 5
    # 序列号
    sequence_bits = 12

    # 最大值计算
    max_machine_id = -1 ^ (-1 << machine_id_bits)  # 用于确保机器ID在范围内
    max_datacenter_id = -1 ^ (-1 << datacenter_id_bits)
    sequence_mask = -1 ^ (-1 << sequence_bits)  # 序列号掩码，用于归零

    # 位移计算
    machine_id_shift = sequence_bits
    datacenter_id_shift = sequence_bits + machine_id_bits
    timestamp_left_shift = sequence_bits + machine_id_bits + datacenter_id_bits

    def __init__(self, machine_id, datacenter_id):
        # 健壮性检查：确保传入的机器ID和数据中心ID在合法范围内
        if machine_id > self.max_machine_id or machine_id < 0:
            raise ValueError("Machine ID should be in range 0 to {}".format(self.max_machine_id))
        if datacenter_id > self.max_datacenter_id or datacenter_id < 0:
            raise ValueError("Datacenter ID should be in range 0 to {}".format(self.max_datacenter_id))

        self.machine_id = machine_id
        self.datacenter_id = datacenter_id
        self.sequence = 0  # 初始序列号
        self.last_timestamp = -1  # 初始化上次时间戳

        # 添加一个锁来控制多线程环境下的生成
        self.lock = threading.Lock()

    def _next_timestamp(self, last_timestamp):
        """等待直到下一毫秒时间戳"""
        timestamp = self._current_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._current_timestamp()
        return timestamp

    def _current_timestamp(self):
        """获取当前的时间戳 (单位是毫秒)"""
        return int(time.time() * 1000) - self.epoch

    def generate_id(self):
        """生成Snowflake ID"""
        with self.lock:
            timestamp = self._current_timestamp()

            # 如果当前时间小于上一次ID生成的时间戳，说明系统时钟回拨该抛出异常
            if timestamp < self.last_timestamp:
                raise Exception("Clock moved backwards. Refusing to generate id")

            # 如果是同一时间生成的，则进行毫秒内序列
            if self.last_timestamp == timestamp:
                self.sequence = (self.sequence + 1) & self.sequence_mask
                # 毫秒内序列溢出
                if self.sequence == 0:
                    # 阻塞到下一个毫秒,获得新的时间戳
                    timestamp = self._next_timestamp(self.last_timestamp)
            else:
                # 时间戳改变，毫秒内序列重置
                self.sequence = 0

            self.last_timestamp = timestamp

            # 移位并通过或运算拼到一起组成64位的ID
            return ((timestamp << self.timestamp_left_shift) |
                    (self.datacenter_id << self.datacenter_id_shift) |
                    (self.machine_id << self.machine_id_shift) |
                    self.sequence)
