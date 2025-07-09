import sqlite3
import os

def print_common_values(db_path, table1, table2, column):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 使用 INTERSECT 查询两个表共有的值
    query = f"SELECT {column} FROM {table1} INTERSECT SELECT {column} FROM {table2}"
    cursor.execute(query)
    
    # 打印所有共同值，去除序号，统计总数
    results = cursor.fetchall()
    total = len(results)
    for row in results:
        print(row[0])
    print("\033[1;36m============================================\033[0m")  # 青色高亮打印
    db_name = os.path.basename(db_path)
    # db_name, table1, table2高亮打印（青色）
    print(f"[\033[1;32m{db_name}\033[0m] ==>> \033[1;32m{table1}\033[0m & \033[1;32m{table2}\033[0m")
    print(f"Total Signer: [\033[1;33m{total}\033[0m]")

    conn.close()

# 使用示例
print_common_values('../DNF.db', 'GOONC', 'KLED', 'Signer')
