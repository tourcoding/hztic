import sqlite3

# 连接到数据库（如果文件不存在，会自动创建）
conn = sqlite3.connect('./test/example.db')

# 创建一个游标对象
cursor = conn.cursor()

# 创建表
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    token_balance INTEGER DEFAULT 0
)
''')

# 提交更改并关闭连接
conn.commit()
conn.close()