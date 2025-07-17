import os
import json
from rich import print
from rich.syntax import Syntax
import time


# 指定KOL
kol = "DNF"
# 指定Symbol，否则遍历
symbol = None
# symbol = "SUBY"
target_file = f"{kol}.json"

base_path = os.path.dirname(os.path.abspath(__file__))
target_path = os.path.join(base_path, 'database', target_file)

# print(target_path)

def friend_print(response):
    json_str = json.dumps(response, indent=4, ensure_ascii=False)
    syntax = Syntax(json_str, "json", theme="dracula", background_color="default")
    print(syntax)

def read_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            return json.load(file)
    except Exception as e:
        print(f"读取或解析JSON失败: {e}")
        return None
    
def write_json_file(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print(f"JSON数据已写入到 {file_path}")
    except Exception as e:
        print(f"写入JSON失败: {e}")

# 读取文件，并返回第一个status为False的Symbol
def get_first_false_symbol(data):
    for key, value in data[kol].items():
        if value["status"] is False:
            return key, value
    return None, None

# # 读取JSON文件
# data = read_json_file(target_path)
# assert(data)
# # 如果不指定symbol，则遍历所有symbol
# # friend_print(data)
# for key, value in data[kol].items():
#     # friend_print(key)
#     status = value["status"]
#     print(f"{key}, status: {status}")
#     # 执行查询
#     if status is False:
#         # 将status设置为True
#         value["status"] = True
#         # friend_print(value)
#         # friend_print(value["token_address"])
#         # friend_print(value["signature"])
#         # friend_print(value["deadline"])
#         # print("==================================================")
# TODO GOONC测试将status设置为TRUE
# TODO 先读取JSON文件的status是否为True，如果是则不再查询，继续下一个
# TODO 查询结束，则将指定的Symbol的status设置为True
# friend_print(data[kol][symbol])

# 循环读取JSON文件，直至所有Symbol的status都为True
while True:
    data = read_json_file(target_path)
    assert(data)
    # 如果指定了symbol，则直接获取该Symbol的值
    if symbol:
        symbol_value = data[kol][symbol]
    else:
        # 获取第一个status为False的Symbol
        symbol, symbol_value = get_first_false_symbol(data)
        # 遍历打印键值对
        for key, value in data[kol].items():
            print(f"{key}, status: {value['status']}")
        if symbol is None:
            print("所有Symbol的status都为True，结束所有查询")
            break
    # TODO 执行查询
    time.sleep(1)  # 模拟查询延时
    symbol_value["status"] = True
    # 将status设置为True，并写入文件里
    write_json_file(target_path, data)
    symbol = None  # 重置symbol，继续下一个查询
