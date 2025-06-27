

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
from enum import Enum

class Platform(str, Enum):
    Helius = "helius"
    Tatum = "tatum"
    Solana = "solana"

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

# 初始化数据库
def init_database(db_name, symbol, record):
    # 连接数据库 # ** 如果数据库不存在会自动新建 
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    # 创建游标
    cursor = conn.cursor()
    # 检查表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (symbol,))
    if cursor.fetchone() is not None:
        # 表存在, 查询最后一条记录
        cursor.execute(f"SELECT * FROM {symbol} ORDER BY ROWID DESC LIMIT 1")
        row = cursor.fetchone()
        last_record = dict(row)
        # print(last_record)
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
                        (record["BlockTime"], record["HumanTime"], record["Signature"], record["Signer"]))
        # 提交事务 # TODO 每次分页查询完整结束后，调用一次commit
        conn.commit()
        # 第一条就是最后一条
        last_record = record
    conn.close()
    return last_record

# TODO 去重，如果出现更早的时间则替换同一个Signer的记录
def insert_records(db_name, record_list):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    for record in record_list:
        cursor.execute(f"INSERT INTO {symbol} (BlockTime, HumanTime, Signature, Signer) VALUES (?, ?, ?, ?)",
                        (record["BlockTime"], record["HumanTime"], record["Signature"], record["Signer"]))
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
    
def get_signer(url, headers, params, signature):
    response = get_transaction(url, headers, params, signature)
    # friend_print(response)
    # TODO 添加容错处理
    if 'result' in response:
        # 获取Signer地址(买入地址)  
        first_account_key = response["result"]["transaction"]["message"]["accountKeys"][0]
    else:
        print("======= Error =======")
        friend_print(response)
        first_account_key = None
    return first_account_key

def get_signatures_for_address_list(url, headers, params, address, signature, num):
    # 查询结果
    response = get_signatures_for_address(url, headers, params, address, signature, num)
    # 打印结果
    # friend_print(response)
    # ** 如果"err"不为null，说明交易异常，则忽略该签名
    results = []
    for transaction in response.get("result", []):
        if transaction.get("err") is None:
            block_time = transaction.get("blockTime")
            signature = transaction.get("signature")
            results.append((block_time, signature))
    return results


########################## 补充初始数据 ##################################
# https://solscan.io/ 根据哈希签名查询其他需要补充数据
# 签名哈希
signature = "451ruFuMpaPHd1HZw44CfhqzqdJ3h4qgkdCK6Zbx2ro4ZHQMjm55mrSYG82qudXry9SihBbKQ7VqoyYt9miPBozL"
# 代币地址 # ? 暂时无法通过签名哈希查询出代币地址
token_address = "1zJX5gRnjLgmTpq5sVwkq69mNDQkCemqoasyjaPW6jm"
# 车头昵称
kol_nickname = "DNF"

########################## 主函数调用 ####################################
# 选择平台 # ! solana.com接口有速率限制，连续请求必须间隔5秒以上
platform = Platform.Helius
# 初始化RPC接口
rpc_api = rpc_api_map[platform]
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
record = {"BlockTime":block_time, "HumanTime":human_time, "Signature": signature, "Signer":signer}
# print(record)
# 拼接数据库名称
db_name = kol_nickname + ".db"
# print("database_name:", db_name)
symbol = get_symbol(token_address)
# print("table_name:", symbol)
# 初始化数据库,并获取最后一条记录
last_record = init_database(db_name, symbol, record)
# TODO 当时间没有达到指定范围时，每次100个循环查询写入
# ! 先查询一小时
target_block_time = last_record["BlockTime"] + (1 * 3600) 
while target_block_time > last_record["BlockTime"]:
    # 不断更新最后一条记录的时间
    last_record = init_database(db_name, symbol, record)
    # print(last_record)
    signature = last_record["Signature"]
    print("The last Signature is:",signature)
    # 查询列表
    results = get_signatures_for_address_list(url, headers, params, token_address, signature, 100)
    record_list = []
    print(f"Expect Signatures List Length: {len(results)}")
    # 打印列表 
    for i, (block_time, signature) in enumerate(results, start=1):
        if platform == "solana":
            time.sleep(5)
        # 获取Signer地址 
        signer = get_signer(url, headers, params, signature)
        # TODO 添加容错处理
        if signer is None:
            print("[Error]: Get Signer Failed, stop...")
            break
        # 转换为可读的UTC时间 # ! 默认0时区，即 +UTC
        human_time = datetime.fromtimestamp(block_time, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{i:03d}] BlockTime: {block_time}, HumanTime: {human_time}, Signature: {signature}, Signer: {signer}")
        record_list.append({"BlockTime":block_time, "HumanTime":human_time, "Signature": signature, "Signer":signer})
        if i == len(results):
            print("=======================================")
            print("Every valid data requst success, inserting database...")
            insert_records(db_name, record_list)
            print("Inserting done, now wait 5s to continue or stpp manually")
            time.sleep(5)

if target_block_time < last_record["BlockTime"]:
    print("All Success")
    print("target_block_time",target_block_time)
    print("last_record_BlockTime", last_record["BlockTime"])

