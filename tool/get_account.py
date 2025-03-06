import okx.Account as Account
from rich import print_json
################### API KEY初始化 ###########################
import sys, json
from pathlib import Path

apikey = ""
secretkey = ""
passphrase = ""

# 读取API Key等内容
def read_api_key_data():
    current_dir = Path.cwd()
    for file in current_dir.rglob("api_key.json"):
        # print(f"Found: {file}")
        try:
            with open(file, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
                # print("Parsed JSON:", data)
                return data
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            sys.exit(1)
    print("api_key.json not found")
    sys.exit(1)

# 读取API Key等内容
api_key_data = read_api_key_data()
# 赋值本地变量
apikey = api_key_data['apikey']
secretkey = api_key_data['secretkey']
passphrase = api_key_data['passphrase']
#############################################################

flag = "0"  # 实盘:0 , 模拟盘:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)
# 查看账户余额
result = accountAPI.get_account_balance()
# 查看持仓信息
json_str = json.dumps(result)
print_json(json_str)
