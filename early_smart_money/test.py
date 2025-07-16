import os
import json
from rich import print
from rich.syntax import Syntax


# 指定KOL
kol = "DNF"
# 指定Symbol，否则遍历
symbol = None
# symbol = "Ani"
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

# 读取JSON文件
data = read_json_file(target_path)
if data:
    # 打印JSON内容
    if symbol is None:
        # friend_print(data)
        for key, value in data[kol].items():
            if value["status"] is False:
                friend_print(key)
                # friend_print(value)
                friend_print(value["token_address"])
                friend_print(value["signature"])
                friend_print(value["deadline"])
                print("==================================================")
    else:
        friend_print(data[kol][symbol])

