import sqlite3
import os

def print_common_values(db_path, table1, table2):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 使用 INTERSECT 查询两个表共有的值
    query = f"SELECT Signer FROM {table1} INTERSECT SELECT Signer FROM {table2}"
    cursor.execute(query)
    
    # 打印所有共同值，去除序号，统计总数
    results = cursor.fetchall()
    total = len(results)
    for row in results:
        print(row[0])
    print("\033[1;36m=================================================\033[0m")  # 青色高亮打印
    db_name = os.path.basename(db_path)
    # db_name, table1, table2高亮打印（青色）
    print(f"\033[1;32m{db_name}\033[0m")
    print("\033[1;36m-------------------------------------------------\033[0m")  # 青色高亮打印

    # 查询每个表的时间范围
    def get_time_range(table):
        # 查询最晚的BlockTime和HumanTime
        query = f"SELECT BlockTime, HumanTime FROM {table} ORDER BY rowid ASC LIMIT 1"
        cursor.execute(query)
        max_block_time, max_human_time = cursor.fetchone()
        # 查询最早的BlockTime和HumanTime
        query = f"SELECT BlockTime, HumanTime FROM {table} ORDER BY rowid DESC LIMIT 1"
        cursor.execute(query)
        min_block_time, min_human_time = cursor.fetchone()
        return max_block_time, max_human_time, min_block_time, min_human_time
    
    t1_max_bt, t1_max_ht, t1_min_bt, t1_min_ht = get_time_range(table1)
    t2_max_bt, t2_max_ht, t2_min_bt, t2_min_ht = get_time_range(table2)

    # 计算时间差
    def calc_time_cost(start, end):
        seconds = end - start
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours:02d}h:{minutes:02d}m"

    t1_cost = calc_time_cost(t1_min_bt, t1_max_bt)
    t2_cost = calc_time_cost(t2_min_bt, t2_max_bt)

    # 打印表名和时间范围
    print(f"\033[1;32m{table1}\t[{t1_min_ht} - {t1_max_ht}], {t1_cost}\033[0m")
    print(f"\033[1;32m{table2}\t[{t2_min_ht} - {t2_max_ht}], {t2_cost}\033[0m")
    print(f"Total Signer: [\033[1;33m{total}\033[0m]")

    conn.close()

# 使用示例
db_name = "DNF.db"
base_path = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_path, 'database', db_name)

# 读取数据库的表名
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]
print(tables)
conn.close()
# 比较不同的tables
print_common_values(db_path, tables[0], tables[1])
print_common_values(db_path, tables[1], tables[2])
print_common_values(db_path, tables[0], tables[2])
# 
