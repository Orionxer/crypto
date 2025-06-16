
# TODO 实现分页查询，验证分页是否正确
# TODO 查询所有记录
# TODO 将查询结果保存到文件中
import requests
from rich import print
from rich.syntax import Syntax
import json
import time

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
for i, (block_time, signature) in enumerate(results, start=1):
    # 获取Signer地址
    signer = get_signer(signature)
    print(f"[{i:03d}] blockTime: {block_time}, signature: {signature}, signer: {signer}")
    time.sleep(5)
