﻿################## 输入内容 ##################
# 1. 哈希签名 
# 2. 代币地址
# 3. 车头昵称
# 4. 需要查询的时间范围

######################## 流程概述 #########################
# 根据代币地址查询代币名称
# 连接车头昵称命名的数据库(如果不存在则自动新建)，例如"DNF.db"
# 读取数据库表最后一条数据，获取区块信息，如果为空说明是新表
# 根据最后一个Block区号继续向前查询，将查询结果写入数据库
# 只有到达指定的时间范围才能停止向前查询

import sqlite3
import requests
from rich import print
from rich.syntax import Syntax
import json
import time
from datetime import datetime, timezone
from enum import Enum

# 【x] 切换不同RPC接口的URL及其密钥(额度耗尽时可以切换)
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
# 初始化数据库
def init_database(db_name, symbol, record):
    if symbol is None or record is None:
        return
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
                Block     INTEGER,
                BlockTime INTEGER,
                HumanTime TEXT,
                SOL       REAL,
                Token     REAL,
                Signature TEXT,
                Signer TEXT
            )
        ''')
        # 插入第一条数据
        cursor.execute(f"INSERT INTO {symbol} \
                       (Block, BlockTime, HumanTime, SOL, Token, Signature, Signer) \
                       VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (
                            record["Block"], 
                            record["BlockTime"], 
                            record["HumanTime"],
                            record["SOL"],
                            record["Token"],
                            record["Signature"],
                            record["Signer"]
                        ))
        # 提交事务 # TODO 每次分页查询完整结束后，调用一次commit
        conn.commit()
        # 第一条就是最后一条
        last_record = record
    conn.close()
    return last_record

# * 待定：去重，如果出现更早的时间则替换同一个Signer的记录
def insert_records(db_name, record_list):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    for record in record_list:
        cursor.execute(f"INSERT INTO {symbol} \
                       (Block, BlockTime, HumanTime, SOL, Token, Signature, Signer) \
                       VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (
                            record["Block"], 
                            record["BlockTime"], 
                            record["HumanTime"],
                            record["SOL"],
                            record["Token"],
                            record["Signature"],
                            record["Signer"]
                        ))
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
        return None
    

########################## 查询交易 ####################################

def get_ui_amount(balances, signer):
    for b in balances:
        if b.get("mint") == token_address and b.get("owner") == signer:
            amount_info = b.get("uiTokenAmount", {})
            return amount_info.get("uiAmount", 0.0)
    return 0.0

def get_transaction(url, headers, params, signature):
    result = {}
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
        data = response.json()
        meta = data["result"]["meta"]
        # 获取Slot(Block区块信息)
        slot = data["result"]["slot"]
        # 获取时间
        block_time = data["result"]["blockTime"]
        # 转换可读时间，0时区
        human_time = datetime.fromtimestamp(block_time, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        # 获取签名地址
        signer = data["result"]["transaction"]["message"]["accountKeys"][0]
        # 计算花费的SOL(暂不考虑优先费以及手续费)
        sol_spent = (meta.get("preBalances", [0])[0] - meta.get("postBalances", [0])[0]) / 1e9
        # 获取买入的代币数量
        post_amount = get_ui_amount(meta.get("postTokenBalances", []), signer) or 0.0
        pre_amount = get_ui_amount(meta.get("preTokenBalances", []), signer) or 0.0
        token = post_amount - pre_amount
        result = {"Block":slot, "BlockTime":block_time, "HumanTime":human_time, "SOL":sol_spent, "Token":token,"Signature": signature, "Signer":signer}
        # friend_print(response.json())
        # return response.json()
        return result
    except Exception as e:
        print(f"请求失败：{e}")
        return None
    
def get_block_transactions(url, headers, params, slot):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBlock",
        "params": [
            slot, 
            {
                "encoding": "json",
                "maxSupportedTransactionVersion": 0,
                "transactionDetails": "accounts",
                "rewards": None
            }
        ]
    }
    record_list = {}
    transactions = []
    try:
        response = requests.post(url, params=params, headers=headers, json=payload, timeout=10)
        data = response.json()
        block_time = data["result"]["blockTime"]
        parent_slot = data["result"]["parentSlot"]
        human_time = datetime.fromtimestamp(block_time, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        for tx in data["result"]["transactions"]:
            meta = tx.get("meta", {})
            tx_data = tx.get("transaction", {})
            account_keys = tx_data.get("accountKeys", [])
            signature_list = tx_data.get("signatures", [])

            # 判断交易是否涉及目标代币
            balances = meta.get("postTokenBalances", []) + meta.get("preTokenBalances", [])
            if not any(b.get("mint") == token_address for b in balances):
                continue

            # 获取交易发起地址信息 # 生成器表达式+next函数组合，用于找到第一个满足条件的元素
            signer_info = next((a for a in account_keys if a.get("signer")), None)
            if not signer_info:
                continue
            signer = signer_info["pubkey"]

            # 获取交易发起地址在余额数组中的索引
            try:
                # 列表推导式，将地址合并为列表后进行定位交易发起地址
                signer_index = [a["pubkey"] for a in account_keys].index(signer)
            except ValueError:
                continue

            post_amount = get_ui_amount(meta.get("postTokenBalances", []), signer) or 0.0
            pre_amount = get_ui_amount(meta.get("preTokenBalances", []), signer) or 0.0
            token = post_amount - pre_amount
            # * 缺少代币创建哈希，但不影响功能。可以通过getSignatureForAddress查询到哈希签名后去solscan验证
            # 判断是否是买入行为（余额增加）
            if post_amount > pre_amount:
                # preBalances[0] 和 postBalances[0] 代表SOL余额，单位 Lamports
                sol_spent = (meta.get("preBalances", [0])[signer_index] - meta.get("postBalances", [0])[signer_index]) / 1e9
                # print(signature_list[0], signer, f"Token: {post_amount - pre_amount}", f"SOL: {sol_spent:.6f}")
                record = {
                    "ParentBlock": parent_slot,
                    "Block":slot,
                    "BlockTime":block_time,
                    "HumanTime":human_time,
                    "SOL":sol_spent,
                    "Token":token,
                    "Signature": signature_list[0],
                    "Signer":signer
                }
                transactions.append(record)
        record_list = {
            "ParentBlock": parent_slot, 
            "Block": slot, 
            "BlockTime": block_time, 
            "HumanTime": human_time, 
            "transactions": list(reversed(transactions))
            } # 反转列表
        return record_list
    except Exception as e:
        print(f"请求失败：{e}")
        return None

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
# 查询车头第一次买入
record = get_transaction(url, headers, params, signature)
if record is None: exit()
# 拼接数据库名称
db_name = kol_nickname + ".db"
# 获取代币名称（表名）
symbol = get_symbol(token_address)
if symbol is None: exit()
# 初始化数据库,并获取最后一条记录
last_record = init_database(db_name, symbol, record)
# print(last_record)
record_list = get_block_transactions(url, headers, params, last_record["Block"])
if record_list is None: exit()
# print(record_list)

# 从头开始找目标哈希签名
transacion_list = record_list["transactions"]
i = next((idx for idx, d in enumerate(transacion_list) if d.get('Signature') == last_record["Signature"]), None)
start = i + 1 if i is not None else 0
# 如果数据库最新的哈希不是当前区块的最后一个哈希，则位于目标哈希前的哈希插入数据库
if start < len(transacion_list):
    new_list = transacion_list[start:]
    insert_records(db_name, new_list)
# 如果目标哈希是当前区块的最后一个签名，则说明数据块完整存储了区块信息
# 获取上一个Block
parent_block = record_list["ParentBlock"]
start_time = record_list["BlockTime"]
# 指定查询结束的时间 # ? 时间可以参考GMGN的初始时间进行适当设置
end_time = start_time - 3600
while start_time > end_time:
    # 获取上一个区块的交易信息
    record_list = get_block_transactions(url, headers, params, parent_block)
    if record_list is None:
        # 可能是网络接口限制原因，等待5秒后重试
        print(f"Retrying after 5 seconds...")
        time.sleep(5)
        continue
    start_time = record_list["BlockTime"]
    parent_block = record_list["ParentBlock"]
    if not record_list["transactions"]:
        print(f"Skip Block: {record_list['Block']} - Time: {record_list['HumanTime']} - No transactions found for {symbol}")
        continue
    # 打印当前区块的交易记录
    for record in record_list["transactions"]:
        print(f"Time: {record['HumanTime']}, SOL: {record['SOL']}, Signature: {record['Signature']}, Signer: {record['Signer']}")
    # 插入新查询的记录
    insert_records(db_name, record_list["transactions"])

print("=========================================")
print("Successfully completed the query")
