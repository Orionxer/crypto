

# TODO 切换不同RPC接口的URL及其密钥(额度耗尽时可以切换)

##################### 流程概述 ######################
# 传入的参数为哈希签名以及车头昵称，以及需要查询的时间范围
# 根据哈希签名查询代币地址，根据代币地址查询代币名称
# 连接车头昵称+代币命名的数据库(如果不存在则自动新建)
# 读取数据库最后一条记录，获取Unix时间戳和交易哈希
    # 如果数据库为空说明是第一次新建
# 根据最后一个交易哈希进行开始分页查询，并将结果插入数据库
    # 查询结束条件(或)
        # 达到规定的时间范围
        # 已经查询到该代币的第一条交易数据

import sqlite3
import requests
from rich import print
from rich.syntax import Syntax
import json
import time
from datetime import datetime, timezone

############################ 数据库 #####################################
# def create_database():
# 拼接数据库名称
db_name = "DNF"+ ".db"
symbol = "GOONC"

# 连接数据库 # ** 如果数据库不存在会自动新建 
conn = sqlite3.connect(db_name)

# 创建游标对象
cursor = conn.cursor()

# 检查表是否存在
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (symbol,))
if cursor.fetchone() is not None:
    print("表存在") 
    #TODO 查询最后一条记录
else:
    print("表不存在")

# 创建表
cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {symbol} (
        BlockTime INTEGER,
        HumanTime TEXT,
        Signature TEXT,
        Signer TEXT
    )
''')

# # 向指定的表插入一条数据
# cursor.execute(f"INSERT INTO {symbol} (BlockTime, HumanTime, Signature, Signer) VALUES (?, ?, ?, ?)",
#                 (1747103065, "2025-05-13 02:24:25", "AAR9fAXWRUzr8YpUQgbxMBqtS92duY5bdWoGoGJxW3ZJeZSxSwdLpThPfTAdnh6BqQGqJhhSrUR6dnpr9hnyQfT", "BB4z2R9J1MVhr35sbmapsfohym4xmkVXDj3dyNZW6yCz"))

# # 提交事务 # TODO 每次分页查询完整结束后，调用一次commit
# conn.commit()

# 查询最后一条记录
cursor.execute(f"SELECT * FROM {symbol} ORDER BY ROWID DESC LIMIT 1")
last_record = cursor.fetchone()
print(last_record)

conn.close()

########################## 补充初始数据 ##################################
# 签名哈希
signature = "GF5tJVe6PZV2DFVhSYRZQSxisoH9YS8fTnGGwBqNcCYJ1jmyBr5VRVcKJRJRsK9TRsyrHmX7K1eEvqgPPvXxSBk"
# 车头昵称
kol_nickname = "DNF"

########################## 主函数调用 ####################################
