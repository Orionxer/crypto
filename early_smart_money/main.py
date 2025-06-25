

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

############################ RPC接口 #####################################
rpc_api_map = {
    "helius": {
        "url": "https://mainnet.helius-rpc.com",
        "headers": {
            "accept": "application/json",
            "content-type": "application/json"
        },
        "params": {
            "api-key": "99068046-8305-4d16-9c03-b7e6ae63250b"
        }
    },
    "tatum": {
        "url": "https://solana-mainnet.gateway.tatum.io/",
        "headers": {
            "accept": "application/json",
            "content-type": "application/json",
            "x-api-key": "t-66a730ccccfd17001c479705-2f597d14ad7543f289a03418"
        },
        "params": {}
    },
    "solana": {
        "url": "https://api.mainnet-beta.solana.com",
        "headers": {
            "content-type": "application/json",
        },
        "params": {}
    }
}

############################ 优化打印 #####################################
def friend_print(response):
    json_str = json.dumps(response, indent=4, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="dracula", background_color="default")
    print(syntax)

############################ 数据库 #####################################
# def create_database():

record = {}
record_list = []

# 初始化数据库
def init_database(db_name, symbol, record_list):
    # 连接数据库 # ** 如果数据库不存在会自动新建 
    conn = sqlite3.connect(db_name)
    # 创建游标
    cursor = conn.cursor()
    # 检查表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (symbol,))
    if cursor.fetchone() is not None:
        # 表存在, 查询最后一条记录
        cursor.execute(f"SELECT * FROM {symbol} ORDER BY ROWID DESC LIMIT 1")
        last_record = cursor.fetchone()
        print(last_record)
    else:
        # 表不存在，创建一个新表
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {symbol} (
                BlockTime INTEGER,
                HumanTime TEXT,
                Signature TEXT,
                Signer TEXT
            )
        ''')
        # 插入第一条数据
        cursor.execute(f"INSERT INTO {symbol} (BlockTime, HumanTime, Signature, Signer) VALUES (?, ?, ?, ?)",
                        (1747103065, "2025-05-13 02:24:25", "AAR9fAXWRUzr8YpUQgbxMBqtS92duY5bdWoGoGJxW3ZJeZSxSwdLpThPfTAdnh6BqQGqJhhSrUR6dnpr9hnyQfT", "BB4z2R9J1MVhr35sbmapsfohym4xmkVXDj3dyNZW6yCz"))
        # 提交事务 # TODO 每次分页查询完整结束后，调用一次commit
        conn.commit()
    conn.close()


########################## 查询Symbol ##################################
# 文档 ： https://docs.tatum.io/reference/gettokensv4
def get_symbol(token_address):
    url = "https://api.tatum.io/v4/data/tokens"
    headers = {
        "accept": "application/json",
        "x-api-key": "t-685a3f207b2cac50cedeba6f-0543689c7fa6497bbcf314bc"
    }
    params = {
        "chain": "solana",
        "tokenAddress": token_address
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        # print(response.json())
        return response.json()["symbol"]
    except Exception as e:
        print(f"请求失败：{e}")
        return {"error": str(e)}
    

########################## 查询交易 ####################################

def get_transaction(url, headers, params, signature):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            signature,
            {
                "commitment": "confirmed",
                "maxSupportedTransactionVersion": 0,
                "encoding": "json"
            }
        ]
    }
    try:
        response = requests.post(url, params=params, headers=headers, json=payload, timeout=10)
        # friend_print(response.json())
        return response.json()
    except Exception as e:
        print(f"请求失败：{e}")
        return {"error": str(e)}

# 查询指定交易哈希之前的交易哈希列表
def get_signatures_for_address(url, headers, params, address, signature, num):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            address,
            {
                "limit": num,
                "before": signature
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, params=params, json=payload, timeout=10)
        return response.json()
    except requests.exceptions.Timeout:
        print("请求超时")
        return {"error": "timeout"}
    except requests.exceptions.RequestException as e:
        print(f"请求失败：{e}")
        return {"error": str(e)}

########################## 补充初始数据 ##################################
# https://solscan.io/ 根据哈希签名查询其他需要补充数据
# 签名哈希
signature = "GF5tJVe6PZV2DFVhSYRZQSxisoH9YS8fTnGGwBqNcCYJ1jmyBr5VRVcKJRJRsK9TRsyrHmX7K1eEvqgPPvXxSBk"
# 代币地址 # ? 暂时无法通过签名哈希查询出代币地址
token_address = "ENfpbQUM5xAnNP8ecyEQGFJ6KwbuPjMwv7ZjR29cDuAb"
# 车头昵称
kol_nickname = "DNF"

########################## 主函数调用 ####################################
# 初始化RPC接口 # ! solana.com接口有速率限制，连续请求必须间隔5秒以上
rpc_api = rpc_api_map["helius"]
url = rpc_api["url"]
headers = rpc_api["headers"]
params = rpc_api["params"]
# record = get_signatures_for_address(url, headers, params, token_address, signature, 1)
# 查询车头第一次买入
response = get_transaction(url, headers, params, signature)
# 获取时间
block_time = response["result"]["blockTime"]
# 转换可读时间，0时区
human_time = datetime.fromtimestamp(block_time, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
# 获取买入地址
signer = response["result"]["transaction"]["message"]["accountKeys"][0]
record_list = [
    {"BlockTime":block_time, "HumanTime":human_time, "Signature": signature, "Signer":signer},
]
print(record_list)
# 拼接数据库名称
db_name = kol_nickname + ".db"
# print("database_name:", db_name)
symbol = get_symbol(token_address)
# print("table_name:", symbol)

