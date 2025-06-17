
# TODO 实现分页查询，验证分页是否正确
# TODO 查询所有记录
# TODO 将查询结果保存到文件中
import requests
from rich import print
from rich.syntax import Syntax
import json
import time
from datetime import datetime, timezone

# 导入外部接口
from getSignaturesForAddress import get_signatures_for_address_list
from getTransaction import get_signer

# 使用示例
# 签名哈希
signature = "GF5tJVe6PZV2DFVhSYRZQSxisoH9YS8fTnGGwBqNcCYJ1jmyBr5VRVcKJRJRsK9TRsyrHmX7K1eEvqgPPvXxSBk"
# 代币合约地址
token_address = "ENfpbQUM5xAnNP8ecyEQGFJ6KwbuPjMwv7ZjR29cDuAb"
# 查询列表
results = get_signatures_for_address_list(token_address, signature)
# 打印列表 
# TODO 添加本地超时
# TODO 添加容错处理
for i, (block_time, signature) in enumerate(results, start=1):
    # 获取Signer地址
    signer = get_signer(signature)
    # 转换为可读的UTC时间 # ! 默认0时区，即 +UTC
    human_time = datetime.fromtimestamp(block_time, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{i:03d}] BlockTime: {block_time}, HumanTime: {human_time}, Signature: {signature}, Signer: {signer}")
    time.sleep(5)
