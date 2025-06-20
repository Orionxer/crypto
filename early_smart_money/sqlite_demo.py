import sqlite3

# 1. 连接数据库（如果文件不存在会自动创建）
conn = sqlite3.connect('example.db')

# 2. 创建一个游标对象
cursor = conn.cursor()

# 3. 创建一个表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER
    )
''')

# 4. 插入一条数据
cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("Alice", 25))

# 5. 查询数据
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
for row in rows:
    print(row)

# 6. 提交事务并关闭连接
conn.commit()
conn.close()
