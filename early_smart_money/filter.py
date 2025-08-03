import sqlite3
import os
import unicodedata

# 计算时间差
def calc_time_cost(start, end):
    seconds = end - start
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:02d}h:{minutes:02d}m"

# 查询表的时间范围
def get_time_range(db_path, table):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询最早的BlockTime和HumanTime
    query = f"SELECT BlockTime, HumanTime FROM {table} ORDER BY rowid ASC LIMIT 1"
    cursor.execute(query)
    min_block_time, min_human_time = cursor.fetchone()
    
    # 查询最晚的BlockTime和HumanTime
    query = f"SELECT BlockTime, HumanTime FROM {table} ORDER BY rowid DESC LIMIT 1"
    cursor.execute(query)
    max_block_time, max_human_time = cursor.fetchone()
    
    conn.close()
    return max_block_time, max_human_time, min_block_time, min_human_time

# 打印所有表名以及输出对应的时间范围
def display_all_table(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    # 打印所有表名
    print("\033[1;36m====================\033[0m")  # 青色高亮打印
    db_name = os.path.basename(db_path)
    print(f"\033[1;32m{db_name}\033[0m")
    print("\033[1;36m--------------------\033[0m")  # 青色高亮打印
    
    def pad_display(s, width):
        w = 0
        for c in s:
            w += 2 if unicodedata.east_asian_width(c) in 'WF' else 1
        return s + ' ' * (width - w)
    
    for table in tables:
        max_bt, max_ht, min_bt, min_ht = get_time_range(db_path, table)
        print(f"\033[1;32m{pad_display(table, 20)}[{min_ht} - {max_ht}], {calc_time_cost(max_bt, min_bt)}\033[0m")
    
    conn.close()

# SQlite跨表查询，查找至少n个表中共同的值, seperator默认为空格
def find_common_signers(db_path, n, seperator=" "):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    # 字典存储每个Signer出现的表
    signer_tables = {}
    
    # 遍历所有表
    for table in tables:
        try:
            # 查询当前表的去重Signer
            cursor.execute(f"SELECT DISTINCT Signer FROM {table} WHERE Signer IS NOT NULL")
            signers = [row[0] for row in cursor.fetchall()]
            
            # 更新字典
            for signer in signers:
                signer_tables.setdefault(signer, []).append(table)
                
        except sqlite3.OperationalError:
            continue  # 跳过不包含Signer列的表
    
    # 早期聪明钱列表
    early_signers_list = []
    # 筛选并打印结果, 排序，len(table_list) 越大越靠前
    for signer, table_list in sorted(signer_tables.items(), key=lambda x: len(x[1]), reverse=True):
        if len(table_list) >= n:
            # 对齐输出
            max_len = max(len(signer) for signer in signer_tables.keys())
            print(f"{signer.ljust(max_len)}: {[len(table_list)]} {', '.join(table_list)}")
            # 缓存早期聪明钱
            early_signers_list.append((signer, len(table_list)))
    print("\033[1;36m====================\033[0m")  # 青色高亮打印
    # 删除第一个元素
    early_signers_list.pop(0)
    # 打印早期聪明钱总数
    print(f"\033[1;32m早期聪明钱总数: {len(early_signers_list)}\033[0m")
    print("\033[1;36m====================\033[0m")  # 青色高亮打印
    # 打印早期聪明钱列表
    for i, signer in enumerate(early_signers_list, start=1):
        # 只输出序号
        print(f"{signer[0]}{seperator}{i}")
        # 输出序号和重复的表数
        # print(f"{signer[0]}{seperator}{i}-{signer[1]}")
    conn.close()

# 使用示例
db_name = "DNF.db"
seperator = ","
base_path = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_path, 'database', db_name)

# 打印所有表名以及输出对应的时间范围
display_all_table(db_path)

# 查找至少n个表中共同的Signer
find_common_signers(db_path, 5, seperator)



