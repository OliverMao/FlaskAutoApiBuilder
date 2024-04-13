from faker import Faker
import pymysql
import random

# 初始化faker生成器
fake = Faker()

# 数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'g7055123',
    'database': 'test'
}

# 连接到数据库
connection = pymysql.connect(**db_config)
cursor = connection.cursor()

# 插入数据的SQL语句
insert_stmt = (
    "INSERT INTO your_table_name (faab_uid, username, password, nickname, is_delete) "
    "VALUES (%s, %s, %s, %s, %s)"
)

# 生成模拟数据并插入到数据库
try:
    for _ in range(100000):
        # 生成每列的数据
        faab_uid = fake.uuid4()
        username = fake.user_name()
        password = fake.password()
        nickname = fake.first_name()
        is_delete = random.randint(0, 1)
        # 执行插入操作
        cursor.execute(insert_stmt, (faab_uid, username, password, nickname, is_delete))
    # 提交事务
    connection.commit()
except Exception as e:
    print(f"An error occurred: {e}")
    connection.rollback() # 回滚事务
finally:
    # 关闭游标和连接
    cursor.close()
    connection.close()

print("Data insertion complete.")