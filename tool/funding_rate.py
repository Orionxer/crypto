import okx.PublicData as PublicData
import json
from rich import print_json

# flag = "0"  # 实盘:0 , 模拟盘：1

# publicDataAPI = PublicData.PublicAPI(flag=flag)

# # 获取交易产品基础信息
# result = publicDataAPI.get_instruments(
#     instType="SWAP"
# )
# # 打印完整json
# json_str = json.dumps(result)
# print_json(json_str)

# # 获取所有产品ID
# inst_ids = [item["instId"] for item in result.get("data", [])]
# print(json.dumps(inst_ids, indent=4, ensure_ascii=False))

flag = "0"  # 实盘:0 , 模拟盘：1

publicDataAPI = PublicData.PublicAPI(flag=flag)

# 获取永续合约当前资金费率
result = publicDataAPI.get_funding_rate(
    instId="IP-USDT-SWAP",
)
json_str = json.dumps(result)
print_json(json_str)
